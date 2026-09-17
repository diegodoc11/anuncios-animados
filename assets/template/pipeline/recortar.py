"""Deja una imagen generada lista para el video: fondo fuera, bordes limpios y tamaño justo.

Tres modos:
  chroma  la imagen se generó sobre un color plano (verde o magenta) → ese color se vuelve transparente.
  luz     la imagen se generó sobre negro (neón, tiza, plano) → lo oscuro se vuelve transparente
          y lo que brilla se conserva, así el trazo luce igual que en el estilo.
  rembg   recorte con inteligencia artificial local (para fotos o cuando el fondo no quedó plano).

Además puede ponerle el "borde de sticker" del estilo y, con --marco, vaciar el centro
de una escenografía para que solo queden los bordes decorados.

Uso:
  python -X utf8 pipeline/recortar.py material/imagenes-originales/rosa.png public/recortes/rosa.png --estilo vintage-50s
  python -X utf8 pipeline/recortar.py origen.png public/escenografia/vintage-50s.png --estilo vintage-50s --marco
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np
from PIL import Image, ImageFilter

from comun import RAIZ, ok, salir

ESTILOS = json.loads((RAIZ / "src" / "estilos.json").read_text(encoding="utf-8"))

ap = argparse.ArgumentParser()
ap.add_argument("entrada")
ap.add_argument("salida")
ap.add_argument("--estilo", required=True)
ap.add_argument("--modo", default="", choices=["", "chroma", "luz", "rembg"])
ap.add_argument("--marco", action="store_true", help="vacía el centro (escenografía)")
ap.add_argument("--borde", type=int, default=-1, help="grosor del borde de sticker (-1 = el del estilo)")
ap.add_argument("--alto", type=int, default=1500, help="alto máximo del recorte")
ap.add_argument("--tolerancia", type=float, default=1.0, help="sube si queda halo de color (1.4, 1.8…)")
args = ap.parse_args()

if args.estilo not in ESTILOS:
    salir(f"Estilo desconocido: {args.estilo}. Hay: {', '.join(ESTILOS)}")
estilo = ESTILOS[args.estilo]
modo = args.modo or estilo["recorte"]["modo"]
entrada = pathlib.Path(args.entrada)
salida = pathlib.Path(args.salida)
if not entrada.exists():
    salir(f"No encuentro {entrada}")
salida.parent.mkdir(parents=True, exist_ok=True)

im = Image.open(entrada).convert("RGBA")
rgb = np.asarray(im, dtype=np.float32)[:, :, :3]


def alfa_por_chroma(rgb: np.ndarray, tolerancia: float) -> tuple[np.ndarray, np.ndarray]:
    """Color del fondo = el que domina el marco de la imagen. Devuelve (rgb sin mezcla, alfa 0..1)."""
    h, w, _ = rgb.shape
    anillo = np.concatenate([
        rgb[:6].reshape(-1, 3), rgb[-6:].reshape(-1, 3),
        rgb[:, :6].reshape(-1, 3), rgb[:, -6:].reshape(-1, 3),
    ])
    clave = np.median(anillo, axis=0)
    dist = np.linalg.norm(rgb - clave, axis=2)
    t0, t1 = 60 * tolerancia, 145 * tolerancia
    a = np.clip((dist - t0) / max(1.0, t1 - t0), 0, 1)
    # Deshacer la mezcla con el fondo en los bordes suaves (quita el halo de color).
    seguro = np.maximum(a, 1e-3)[:, :, None]
    limpio = np.clip((rgb - (1 - seguro) * clave) / seguro, 0, 255)
    return limpio, a


def alfa_por_luz(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Fondo negro: el brillo se convierte en opacidad (el trazo luminoso se conserva)."""
    maximo = rgb.max(axis=2)
    a = np.clip(maximo / 255.0, 0, 1) ** 0.85
    seguro = np.maximum(a, 1e-3)[:, :, None]
    limpio = np.clip(rgb / seguro, 0, 255)
    return limpio, a


if modo == "rembg":
    try:
        from rembg import remove
    except ImportError:
        salir("Falta rembg.  pip install rembg onnxruntime")
    im = remove(im)
    datos = np.asarray(im.convert("RGBA"), dtype=np.float32)
    color, alfa = datos[:, :, :3], datos[:, :, 3] / 255.0
elif modo == "luz":
    color, alfa = alfa_por_luz(rgb)
else:
    color, alfa = alfa_por_chroma(rgb, args.tolerancia)

recorte = Image.fromarray(
    np.dstack([color.astype(np.uint8), (alfa * 255).astype(np.uint8)]), "RGBA"
)

if args.marco:
    # Escenografía: el centro se vacía para que se vea el fondo y las escenas.
    w, h = recorte.size
    mascara = Image.new("L", (w, h), 255)
    from PIL import ImageDraw

    d = ImageDraw.Draw(mascara)
    d.rectangle([int(w * 0.085), int(h * 0.055), int(w * 0.915), int(h * 0.945)], fill=0)
    mascara = mascara.filter(ImageFilter.GaussianBlur(int(w * 0.012)))
    alfa_img = recorte.getchannel("A")
    from PIL import ImageChops

    recorte.putalpha(ImageChops.multiply(alfa_img, mascara))
    recorte = recorte.resize((1080, 1920), Image.LANCZOS)
else:
    caja = recorte.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if caja:
        margen = 6
        w, h = recorte.size
        recorte = recorte.crop((max(0, caja[0] - margen), max(0, caja[1] - margen),
                                min(w, caja[2] + margen), min(h, caja[3] + margen)))
    grosor = estilo["recorte"]["grosorBorde"] if args.borde < 0 else args.borde
    color_borde = estilo["recorte"]["borde"]
    if grosor > 0 and color_borde:
        g = grosor
        lienzo = Image.new("RGBA", (recorte.width + 2 * g, recorte.height + 2 * g), (0, 0, 0, 0))
        base = Image.new("L", lienzo.size, 0)
        base.paste(recorte.getchannel("A").point(lambda v: 255 if v > 40 else 0), (g, g))
        crecido = base
        for _ in range(max(1, g // 2)):
            crecido = crecido.filter(ImageFilter.MaxFilter(5))
        crecido = crecido.filter(ImageFilter.GaussianBlur(1.5)).point(lambda v: 255 if v > 100 else 0)
        lienzo.paste(Image.new("RGBA", lienzo.size, color_borde), (0, 0), crecido)
        lienzo.alpha_composite(recorte, (g, g))
        recorte = lienzo
    if recorte.height > args.alto:
        escala = args.alto / recorte.height
        recorte = recorte.resize((max(1, int(recorte.width * escala)), args.alto), Image.LANCZOS)

recorte.save(salida)
ok(f"{salida.name} · {recorte.size[0]}×{recorte.size[1]} · modo {modo}")
