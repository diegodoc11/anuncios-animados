"""Hoja de contacto de los recortes: todas las ilustraciones juntas sobre el fondo del estilo.

Sirve para revisar de un vistazo si el chroma quedó limpio, si el personaje se mantiene igual
en todas las poses y si algún objeto se lee raro (la lección clásica: un objeto dibujado solo,
sin persona ni contexto, puede parecer otra cosa completamente distinta).

Uso:  python -X utf8 pipeline/hoja_contacto.py revision/recortes.png --estilo vintage-50s [slug1 slug2 …]
"""
from __future__ import annotations

import argparse
import json
import pathlib

from PIL import Image, ImageDraw

from comun import RAIZ, RECORTES, ok, salir

ESTILOS = json.loads((RAIZ / "src" / "estilos.json").read_text(encoding="utf-8"))

ap = argparse.ArgumentParser()
ap.add_argument("salida")
ap.add_argument("slugs", nargs="*")
ap.add_argument("--estilo", required=True)
ap.add_argument("--celda", type=int, default=300)
ap.add_argument("--columnas", type=int, default=6)
args = ap.parse_args()

if args.estilo not in ESTILOS:
    salir(f"Estilo desconocido: {args.estilo}")
fondo = ESTILOS[args.estilo]["fondo"]
tinta = ESTILOS[args.estilo]["tinta"]

slugs = args.slugs or sorted(p.stem for p in RECORTES.glob("*.png"))
if not slugs:
    salir(f"No hay recortes en {RECORTES}")

celda = args.celda
columnas = min(args.columnas, len(slugs))
filas = (len(slugs) + columnas - 1) // columnas
hoja = Image.new("RGB", (columnas * celda, filas * (celda + 26)), fondo)
d = ImageDraw.Draw(hoja)
for i, slug in enumerate(slugs):
    ruta = RECORTES / f"{slug}.png"
    if not ruta.exists():
        continue
    im = Image.open(ruta).convert("RGBA")
    im.thumbnail((celda - 14, celda - 14))
    x, y = (i % columnas) * celda, (i // columnas) * (celda + 26)
    hoja.paste(im, (x + (celda - im.width) // 2, y + (celda - im.height) // 2), im)
    d.text((x + 8, y + celda + 6), slug, fill=tinta)

destino = pathlib.Path(args.salida)
destino.parent.mkdir(parents=True, exist_ok=True)
hoja.save(destino)
ok(f"{destino} · {len(slugs)} recortes")
