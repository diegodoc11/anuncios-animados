"""Hoja de contacto de un render: saca frames clave y los pega en una rejilla numerada.

Es el control de calidad visual: se mira la hoja y se detecta al instante si un texto
se sale del marco, si una imagen entra tarde o si un beat quedó vacío.

Uso:
  python -X utf8 pipeline/hoja_frames.py out/a1-borrador.mp4 revision --anuncio a1
  python -X utf8 pipeline/hoja_frames.py out/a1-borrador.mp4 revision 30 90 240 700
Con --anuncio toma 3 frames por beat (entrada, mitad y final) usando el manifest.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess

from PIL import Image, ImageDraw

from comun import DATOS, FPS, correr, ok, salir

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("carpeta")
ap.add_argument("frames", nargs="*", type=int)
ap.add_argument("--anuncio", default="", help="id del anuncio: elige los frames solo")
ap.add_argument("--por-beat", type=int, default=3)
ap.add_argument("--columnas", type=int, default=6)
ap.add_argument("--filas", type=int, default=3)
ap.add_argument("--sin-guias", action="store_true", help="no dibujar las guías del ancho útil")
args = ap.parse_args()

video = pathlib.Path(args.video)
if not video.exists():
    salir(f"No encuentro el video {video}")
salida = pathlib.Path(args.carpeta)
salida.mkdir(parents=True, exist_ok=True)

frames = list(args.frames)
if args.anuncio:
    import json

    manifest = json.loads((DATOS / f"{args.anuncio}.manifest.json").read_text(encoding="utf-8"))
    cursor = 0
    for b in manifest["beats"]:
        largo = b["frames"]
        puntos = [cursor + 14, cursor + largo // 2, cursor + largo - 8][: args.por_beat]
        frames += [max(0, p) for p in puntos]
        cursor += largo
if not frames:
    salir("Dime los frames o pásame --anuncio <id>.")
frames = sorted(set(frames))

# Tamaño real del video (el borrador suele ir a media resolución).
info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                       "stream=width,height", "-of", "csv=p=0", str(video)],
                      capture_output=True, text=True).stdout.strip().split(",")
ancho_video = int(info[0]) if info and info[0].isdigit() else 1080

celda_w, celda_h = 270, 480
seleccion = "+".join(f"eq(n\\,{f})" for f in frames)
for viejo in salida.glob("f*.png"):
    viejo.unlink()
correr(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf",
        f"select='{seleccion}',scale={celda_w}:{celda_h}", "-vsync", "0", str(salida / "f%03d.png")])

imagenes = sorted(salida.glob("f*.png"))
if not imagenes:
    salir("ffmpeg no sacó ningún frame (¿números fuera del video?)")

# Guías del ancho útil (860 px de 1080) para ver si un texto se sale del marco.
margen = round((1080 - 860) / 2 / 1080 * celda_w)
por_hoja = args.columnas * args.filas
hojas = []
for h in range(0, len(imagenes), por_hoja):
    grupo = imagenes[h:h + por_hoja]
    hoja = Image.new("RGB", (args.columnas * celda_w, args.filas * celda_h), "white")
    d = ImageDraw.Draw(hoja)
    for i, p in enumerate(grupo):
        x, y = (i % args.columnas) * celda_w, (i // args.columnas) * celda_h
        hoja.paste(Image.open(p), (x, y))
        if not args.sin_guias:
            d.line([(x + margen, y), (x + margen, y + celda_h)], fill=(255, 0, 90), width=1)
            d.line([(x + celda_w - margen, y), (x + celda_w - margen, y + celda_h)], fill=(255, 0, 90), width=1)
        d.rectangle([x, y, x + 62, y + 18], fill="black")
        d.text((x + 5, y + 4), str(frames[h + i]), fill="white")
    ruta = salida / f"hoja{h // por_hoja + 1}.png"
    hoja.save(ruta)
    hojas.append(ruta)

ok(f"{len(imagenes)} frames en {len(hojas)} hoja(s): " + ", ".join(str(x) for x in hojas))
print("Ábrelas y revisa: textos dentro de las líneas rosadas, imágenes a tiempo, banner visible.")
