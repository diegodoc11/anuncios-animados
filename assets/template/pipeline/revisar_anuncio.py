"""Revisión antes de renderizar: encuentra los errores baratos en 2 segundos.

Verifica:
 · que cada `en="palabra"` exista de verdad en la locución de ese beat (si no, el render se cae);
 · que los recortes, la música y los efectos de sonido que se usan existan en public/;
 · que los titulares y etiquetas quepan en el ancho útil (860 px) sin quedar diminutos;
 · que los beats del guion, el manifest y el archivo de palabras coincidan.

Uso:  python -X utf8 pipeline/revisar_anuncio.py a1
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

from comun import DATOS, GUIONES, PUBLICO, RAIZ, RECORTES, SFX, aviso, normalizar, ok, salir

ap = argparse.ArgumentParser()
ap.add_argument("anuncio")
args = ap.parse_args()

archivo = RAIZ / "src" / "anuncios" / f"{args.anuncio}.tsx"
if not archivo.exists():
    salir(f"No encuentro {archivo}")
codigo = archivo.read_text(encoding="utf-8")

ruta_manifest = DATOS / f"{args.anuncio}.manifest.json"
ruta_palabras = DATOS / f"{args.anuncio}.palabras.json"
if not ruta_manifest.exists() or not ruta_palabras.exists():
    salir("Faltan los tiempos. Corre estimar_tiempos.py (borrador) o apretar_voz.py + transcribir_voz.py (voz real).")
manifest = json.loads(ruta_manifest.read_text(encoding="utf-8"))
palabras = json.loads(ruta_palabras.read_text(encoding="utf-8"))

problemas: list[str] = []
avisos: list[str] = []

# ── beats ───────────────────────────────────────────────────────────────────────
ids_manifest = [b["id"] for b in manifest["beats"]]
for bid in ids_manifest:
    if bid not in palabras:
        problemas.append(f"El beat {bid} no tiene palabras transcritas.")
ruta_guion = GUIONES / f"{args.anuncio}.json"
if ruta_guion.exists():
    ids_guion = [b.get("id") for b in json.loads(ruta_guion.read_text(encoding="utf-8"))["beats"]]
    if ids_guion != ids_manifest:
        avisos.append("El guion y el manifest no tienen los mismos beats (¿cambiaste el guion sin regenerar?).")

# ── anclas: a qué beat pertenece cada trozo de código ───────────────────────────
marcas = [(m.start(), m.group(1)) for m in re.finditer(r'"(' + "|".join(map(re.escape, ids_manifest)) + r')"\s*:', codigo)]
if not marcas:
    avisos.append("No pude ver qué escena es de cada beat: usa el mapa  const escenas: Escenas = { \"id-01\": Beat01, … }")


def beat_en(pos: int) -> str | None:
    actual = None
    for inicio, bid in marcas:
        if inicio <= pos:
            actual = bid
        else:
            break
    return actual


def existe_ancla(bid: str, ancla: str) -> bool:
    m = re.match(r"^(.*?)(?:#(\d+))?\s*([+-]\s*\d+)?$", ancla.strip())
    if not m or not m.group(1):
        return False
    buscadas = [normalizar(x) for x in m.group(1).split() if normalizar(x)]
    cual = int(m.group(2) or 1)
    oidas = [normalizar(p) for p, _ in palabras.get(bid, [])]
    vistas = 0
    for i in range(len(oidas) - len(buscadas) + 1):
        if all(oidas[i + k] == b for k, b in enumerate(buscadas)):
            vistas += 1
            if vistas == cual:
                return True
    return False


# En el mapa de escenas las marcas apuntan al final del archivo; para las anclas
# usamos el orden de aparición de las funciones de cada beat (comentario "── id ·").
comentarios = [(m.start(), m.group(1)) for m in re.finditer(r"//\s*──\s*(" + "|".join(map(re.escape, ids_manifest)) + r")\b", codigo)]
if comentarios:
    marcas = comentarios


for m in re.finditer(r'\ben="([^"]+)"', codigo):
    bid = beat_en(m.start())
    if bid is None:
        avisos.append(f'No sé de qué beat es el ancla en="{m.group(1)}" (ponle el comentario // ── <beat> arriba de su escena).')
        continue
    if not existe_ancla(bid, m.group(1)):
        oidas = " ".join(p for p, _ in palabras.get(bid, []))
        problemas.append(f'[{bid}] en="{m.group(1)}" no existe en la locución.\n      se oyó: {oidas}')

# ── archivos usados ─────────────────────────────────────────────────────────────
for m in re.finditer(r'src="([^"]+)"', codigo):
    ruta = m.group(1)
    completa = PUBLICO / (ruta if "/" in ruta else f"recortes/{ruta}")
    if not completa.exists():
        avisos.append(f"Falta el archivo {completa.relative_to(RAIZ)} (se verá el marcador punteado).")

for m in re.finditer(r'sfx="([^"]+)"', codigo):
    nombre = m.group(1)
    ruta = SFX / (f"{nombre}.wav" if "." not in nombre else nombre)
    if not ruta.exists():
        avisos.append(f"Falta el efecto de sonido {ruta.name} (corre pipeline/crear_sfx.py).")

m = re.search(r'musica:\s*\{\s*src:\s*"([^"]+)"', codigo)
if m and not (PUBLICO / m.group(1)).exists():
    avisos.append(f"Falta la música {m.group(1)} (corre preparar_musica.py) — el anuncio quedará sin música.")

# ── textos que no caben ─────────────────────────────────────────────────────────
FACTOR = 0.42
ANCHO = 860
for m in re.finditer(r"<Titular\b([^>]*)>\s*([^<]{1,300}?)\s*</Titular>", codigo, re.S):
    props, texto = m.group(1), " ".join(m.group(2).split())
    tamano = re.search(r"size=\{(\d+)\}", props)
    pedido = int(tamano.group(1)) if tamano else 140
    largo = max(len(l) for l in texto.split("\\n"))
    cabe = int(ANCHO / (FACTOR * max(1, largo)))
    if cabe < pedido * 0.65:
        avisos.append(f'Titular "{texto[:40]}…" se va a encoger de {pedido} a {cabe}px: acórtalo o pártelo con \\n.')

for m in re.finditer(r"<Etiqueta\b([^>]*)>\s*([^<]{1,400}?)\s*</Etiqueta>", codigo, re.S):
    props, texto = m.group(1), " ".join(m.group(2).split())
    size = int(re.search(r"size=\{(\d+)\}", props).group(1)) if re.search(r"size=\{(\d+)\}", props) else 52
    por_linea = max(8, int(ANCHO / (size * 0.48)))
    lineas = (len(texto) + por_linea - 1) // por_linea
    if lineas > 3:
        avisos.append(f'Etiqueta "{texto[:40]}…" ocuparía {lineas} líneas: déjala en 2 (máx. {por_linea * 2} caracteres).')

# ── resultado ───────────────────────────────────────────────────────────────────
print()
for a in avisos:
    aviso(a)
if problemas:
    print()
    for p in problemas:
        print(f"❌ {p}")
    print(f"\n{len(problemas)} error(es) que romperían el render. Arréglalos y vuelve a revisar.")
    sys.exit(1)
ok(f"{args.anuncio}: anclas, archivos y textos revisados. Listo para renderizar el borrador.")
print(f"  npx remotion render src/index.ts {args.anuncio} out/{args.anuncio}-borrador.mp4 --scale=0.5")
