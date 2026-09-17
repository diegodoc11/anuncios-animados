"""Música de fondo ORIGINAL con Suno (a través de Kie.ai, la misma llave de las imágenes).

Es música generada para ti: no hay derechos de terceros ni riesgo de que Meta te silencie
el anuncio. Cada pedido devuelve 2 versiones para que elijas.

Uso:
  python -X utf8 pipeline/gen_musica.py a1 --estilo vintage-50s          # muestra qué pediría
  python -X utf8 pipeline/gen_musica.py a1 --estilo vintage-50s --si     # genera
  python -X utf8 pipeline/gen_musica.py a1 --estilo-musical "bolero triste, guitarra" --si

Salida: material/musica-original/a1-1.mp3 y a1-2.mp3
Después:  pipeline/preparar_musica.py (la deja al volumen correcto bajo la voz)
"""
from __future__ import annotations

import argparse
import json
import time

from comun import MUSICA_ORIGINAL, RAIZ, crear_carpetas, descargar, llave, ok, pedir, salir

ESTILOS = json.loads((RAIZ / "src" / "estilos.json").read_text(encoding="utf-8"))

ap = argparse.ArgumentParser()
ap.add_argument("slug", help="nombre del anuncio, p.ej. a1")
ap.add_argument("--estilo", default="", help="estilo visual: usa su música sugerida")
ap.add_argument("--estilo-musical", default="", help="descripción libre en inglés")
ap.add_argument("--titulo", default="")
ap.add_argument("--modelo", default="V4_5")
ap.add_argument("--si", action="store_true")
args = ap.parse_args()

estilo_musical = args.estilo_musical
if not estilo_musical:
    if args.estilo not in ESTILOS:
        salir("Dime --estilo <estilo visual> o --estilo-musical \"...\"")
    estilo_musical = ESTILOS[args.estilo]["musica"]

print(f"\nMúsica para «{args.slug}»")
print(f"  estilo: {estilo_musical}")
if not args.si:
    print("\n(no se generó nada) Repite con --si para generar las 2 versiones.")
    raise SystemExit(0)

crear_carpetas()
llaves = {"Authorization": f"Bearer {llave('KIE_API_KEY')}", "Content-Type": "application/json"}
r = pedir("https://api.kie.ai/api/v1/generate", llaves, {
    "customMode": True,
    "instrumental": True,
    "model": args.modelo,
    "style": estilo_musical,
    "title": args.titulo or args.slug,
    "callBackUrl": "https://api.kie.ai/no-callback",
})
tarea = (r.get("data") or {}).get("taskId")
if not tarea:
    salir(f"Suno/Kie no devolvió taskId: {json.dumps(r)[:400]}")
print(f"  tarea: {tarea} (tarda 1–3 minutos)")

for intento in range(90):
    time.sleep(10)
    d = (pedir(f"https://api.kie.ai/api/v1/generate/record-info?taskId={tarea}", llaves).get("data") or {})
    estado = d.get("status")
    print(f"   … {estado}", flush=True)
    if estado == "SUCCESS":
        pistas = (d.get("response") or {}).get("sunoData") or []
        for i, pista in enumerate(pistas, 1):
            url = pista.get("audioUrl") or pista.get("sourceAudioUrl")
            destino = descargar(url, MUSICA_ORIGINAL / f"{args.slug}-{i}.mp3")
            ok(f"{destino.name} · {pista.get('duration')}s · {pista.get('tags')}")
        print("\nEscucha las dos y sigue con:")
        print(f"  python -X utf8 pipeline/preparar_musica.py guiones/{args.slug}.json material/musica-original/{args.slug}-1.mp3")
        break
    if estado and ("FAIL" in estado or "ERROR" in estado):
        salir(f"Falló la música: {json.dumps(d)[:400]}")
else:
    salir("Se acabó la espera. Vuelve a intentar.")
