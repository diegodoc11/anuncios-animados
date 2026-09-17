"""Ilustraciones del anuncio con Nano Banana (Kie.ai), ya en el estilo elegido.

Cómo mantener al MISMO personaje en todo el anuncio:
  1. primero se genera "tipo": "personaje" → la imagen base (cara, ropa, edad);
  2. cada pose usa "tipo": "pose" con "ref": ["personaje-base"] → se manda la imagen base
     como referencia y el modelo respeta la cara y la ropa.

Tipos disponibles:
  personaje    la base del protagonista (se genera con el modelo pro)
  pose         el mismo personaje haciendo otra cosa (necesita "ref")
  objeto       una cosa suelta (reloj, celular, billetes…)
  escenografia el marco decorado de los bordes (centro vacío)

Plan de imágenes: guiones/<anuncio>.imagenes.json
{
  "estilo": "vintage-50s",
  "imagenes": [
    {"slug": "julio-base", "tipo": "personaje", "prompt": "a 62-year-old Colombian coffee seller, grey moustache, brown apron"},
    {"slug": "julio-carrito", "tipo": "pose", "ref": ["julio-base"], "prompt": "serving coffee from a small street cart"},
    {"slug": "celular-video", "tipo": "objeto", "prompt": "a hand holding a phone recording a video"},
    {"slug": "marco", "tipo": "escenografia"}
  ]
}

Uso:
  python -X utf8 pipeline/gen_imagenes.py guiones/ejemplo.imagenes.json          # muestra los prompts (no gasta)
  python -X utf8 pipeline/gen_imagenes.py guiones/ejemplo.imagenes.json --si     # genera
  python -X utf8 pipeline/gen_imagenes.py guiones/ejemplo.imagenes.json --si --solo julio-carrito --rehacer
"""
from __future__ import annotations

import argparse
import base64
import json
import pathlib
import sys
import time
import urllib.request

from comun import (ESCENOGRAFIA, IMAGENES_ORIGINALES, RAIZ, RECORTES, aviso, correr, crear_carpetas,
                   descargar, llave, ok, pedir, salir)

API = "https://api.kie.ai/api/v1/jobs"
SUBIR = "https://kieai.redpandaai.co/api/file-base64-upload"
ESTILOS = json.loads((RAIZ / "src" / "estilos.json").read_text(encoding="utf-8"))
PYTHON = sys.executable  # el mismo intérprete con el que corres este script

ap = argparse.ArgumentParser()
ap.add_argument("plan")
ap.add_argument("--si", action="store_true", help="confirma y genera de verdad")
ap.add_argument("--solo", default="", help="slugs separados por coma")
ap.add_argument("--rehacer", action="store_true")
ap.add_argument("--modelo", default="", help="por defecto: nano-banana-pro para personajes/poses, nano-banana-2 para objetos")
args = ap.parse_args()

ruta_plan = pathlib.Path(args.plan)
if not ruta_plan.exists():
    salir(f"No encuentro el plan {ruta_plan}")
plan = json.loads(ruta_plan.read_text(encoding="utf-8"))
estilo_id = plan.get("estilo")
if estilo_id not in ESTILOS:
    salir(f"El plan no dice un estilo válido. Hay: {', '.join(ESTILOS)}")
estilo = ESTILOS[estilo_id]
crear_carpetas()
solo = [s.strip() for s in args.solo.split(",") if s.strip()]
ruta_resultados = ruta_plan.with_suffix(".resultados.json")
resultados = json.loads(ruta_resultados.read_text(encoding="utf-8")) if ruta_resultados.exists() else {}


def prompt_final(item: dict) -> str:
    fondo = estilo["recorte"]["fondoPrompt"]
    tipo = item.get("tipo", "objeto")
    if tipo == "escenografia":
        return (f"{item.get('prompt') or estilo['promptEscenografia']}. {estilo['promptImagen']}. "
                f"Vertical 9:16 poster border. The decoration stays inside a narrow band along the four outer edges "
                f"(about 9% of the width). The entire central area is completely empty: one flat uniform "
                f"{fondo} rectangle with nothing drawn on it. No text, no letters, no numbers, no logos.")
    encabezado = {
        "personaje": "Full-body character design of ",
        "pose": "The exact same character as in the reference image (same face, same hair, same clothes, same age), now ",
        "objeto": "",
    }.get(tipo, "")
    return (f"{encabezado}{item['prompt']}. {estilo['promptImagen']}. "
            f"One single subject, centered, fully inside the frame with generous empty margin around it. "
            f"Background: one perfectly flat uniform {fondo}, no gradient, no floor, no cast shadow, no texture. "
            f"No text, no letters, no numbers, no watermark, no border.")


def modelo_de(item: dict) -> str:
    if args.modelo:
        return args.modelo
    if item.get("modelo"):
        return item["modelo"]
    return "nano-banana-pro" if item.get("tipo") in ("personaje", "pose") else "nano-banana-2"


def sirve(url: str) -> bool:
    """¿La URL de la imagen todavía se puede descargar? (las de Kie caducan con el tiempo)"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status < 400
    except Exception:
        return False


def subir(archivo: pathlib.Path) -> str:
    """Sube una imagen local a Kie y devuelve una URL usable como referencia."""
    datos = base64.b64encode(archivo.read_bytes()).decode()
    r = pedir(SUBIR,
              {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0",
               "Authorization": f"Bearer {llave('KIE_API_KEY')}"},
              {"base64Data": f"data:image/png;base64,{datos}", "uploadPath": "images/anuncios-animados",
               "fileName": archivo.name})
    url = ((r.get("data") or {}).get("downloadUrl") or (r.get("data") or {}).get("fileUrl") or "")
    if not url:
        salir(f"No pude subir la referencia {archivo.name}: {json.dumps(r)[:300]}")
    return url


def referencias(item: dict) -> list[str]:
    """URL de cada imagen de referencia: primero la que devolvió Kie; si caducó, se vuelve a subir."""
    urls = []
    for ref in item.get("ref") or []:
        guardado = resultados.get(ref) or {}
        local = IMAGENES_ORIGINALES / f"{ref}.png"
        url = guardado.get("url") or guardado.get("subida") or ""
        if url and sirve(url):
            urls.append(url)
            continue
        if local.exists():
            url = subir(local)
            resultados.setdefault(ref, {})["subida"] = url
            urls.append(url)
            continue
        salir(f"La referencia '{ref}' todavía no existe. Genera primero esa imagen.")
    return urls


def generar(item: dict) -> str:
    cuerpo = {
        "model": modelo_de(item),
        "input": {
            "prompt": prompt_final(item),
            "aspect_ratio": item.get("proporcion", "9:16" if item.get("tipo") == "escenografia" else "3:4"),
            "resolution": item.get("resolucion", "2K" if item.get("tipo") == "escenografia" else "1K"),
            "output_format": "png",
        },
    }
    refs = referencias(item)
    if refs:
        cuerpo["input"]["image_input"] = refs
    llaves = {"Authorization": f"Bearer {llave('KIE_API_KEY')}", "Content-Type": "application/json"}
    r = pedir(f"{API}/createTask", llaves, cuerpo)
    tarea = (r.get("data") or {}).get("taskId")
    if not tarea:
        salir(f"Kie no devolvió taskId: {json.dumps(r)[:400]}")
    for intento in range(100):
        time.sleep(4)
        d = (pedir(f"{API}/recordInfo?taskId={tarea}", llaves).get("data") or {})
        estado = d.get("state")
        if estado == "success":
            urls = json.loads(d.get("resultJson") or "{}").get("resultUrls") or []
            if not urls:
                salir(f"Sin URL de resultado: {json.dumps(d)[:300]}")
            return urls[0]
        if estado == "fail":
            salir(f"Falló la generación de {item['slug']}: {d.get('failMsg')}")
        if intento % 5 == 0:
            print(f"    … {estado}", flush=True)
    salir(f"Se acabó la espera generando {item['slug']}")


pendientes = []
for item in plan["imagenes"]:
    if solo and item["slug"] not in solo:
        continue
    destino = RECORTES / f"{item['slug']}.png" if item.get("tipo") != "escenografia" else ESCENOGRAFIA / f"{estilo_id}.png"
    if destino.exists() and not args.rehacer:
        print(f"  ya estaba: {destino.name}")
        continue
    pendientes.append(item)

if not pendientes:
    ok("Todas las imágenes del plan ya están.")
    raise SystemExit(0)

print(f"\nEstilo: {estilo['nombre']}  ·  imágenes por generar: {len(pendientes)}\n")
for item in pendientes:
    print(f"── {item['slug']}  ({item.get('tipo', 'objeto')} · {modelo_de(item)})")
    print(f"   {prompt_final(item)}\n")

if not args.si:
    print("(no se generó nada) Repite con --si para generar. Revisa antes los prompts de arriba.")
    raise SystemExit(0)

# Primero los personajes (las poses los necesitan como referencia).
orden = sorted(pendientes, key=lambda i: 0 if i.get("tipo") == "personaje" else 1)
for item in orden:
    print(f"▶ {item['slug']}…", flush=True)
    url = generar(item)
    original = descargar(url, IMAGENES_ORIGINALES / f"{item['slug']}.png")
    resultados.setdefault(item["slug"], {})["url"] = url
    ruta_resultados.write_text(json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf-8")

    if item.get("tipo") == "escenografia":
        destino = ESCENOGRAFIA / f"{estilo_id}.png"
        extra = ["--marco"]
    else:
        destino = RECORTES / f"{item['slug']}.png"
        extra = []
    correr([PYTHON, "-X", "utf8", str(RAIZ / "pipeline" / "recortar.py"), str(original), str(destino),
            "--estilo", estilo_id, *extra])
    ok(f"{item['slug']} → {destino}")

print("\nRevisa cómo quedaron todas juntas:")
print("  python -X utf8 pipeline/hoja_contacto.py revision-recortes.png --estilo " + estilo_id)
