"""Fotos de personas REALES (el dueño del negocio, el doctor, tú) dentro del anuncio.

Regla de oro: a una persona real NUNCA se le redibuja la cara con IA — pierde el parecido
y se ve raro. Lo que hacemos es quitarle el fondo a la foto verdadera y pasarla al universo
visual del estilo (tramas, duotonos, tiza, neón…). Sigue siendo ella, pero pertenece al anuncio.

Uso:
  python -X utf8 pipeline/foto_real.py material/fotos/dueno.jpg dueno --estilo vintage-50s
  python -X utf8 pipeline/foto_real.py foto.png dueno --estilo cine-negro --ya-recortada --fundido 0.2

Salida: public/recortes/<slug>.png
"""
from __future__ import annotations

import argparse
import json
import pathlib

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps

from comun import RAIZ, RECORTES, crear_carpetas, ok, salir
from imagen_util import (borde_sticker, bordes, duotono, fundido_abajo, grano, gris, limitar_alto,
                         lineas_grabado, medios_tonos, persiana, posterizar_paleta, recortar_bbox)

ESTILOS = json.loads((RAIZ / "src" / "estilos.json").read_text(encoding="utf-8"))


def _mezclar(base: Image.Image, capa: Image.Image, cantidad: float) -> Image.Image:
    return ImageChops.blend(base, capa, cantidad)


def vintage(im: Image.Image) -> Image.Image:
    a = im.getchannel("A")
    g = gris(im, 1.3, 1)
    duo = duotono(g, (58, 28, 22), (250, 238, 212), (196, 92, 70))
    duo = _mezclar(duo, ImageChops.overlay(duo, grano(g.size, 12).convert("RGB")), 0.3)
    duo.putalpha(a)
    return duo


def noir(im: Image.Image) -> Image.Image:
    a = im.getchannel("A")
    g = gris(im, 1.9, 2)
    g = ImageEnhance.Brightness(g).enhance(0.95)
    g = ImageChops.multiply(g, persiana(g.size))
    g = _mezclar(g, ImageChops.overlay(g, grano(g.size, 18)), 0.35)
    return Image.merge("RGBA", (g, g, g, a))


def pizarron(im: Image.Image) -> Image.Image:
    a = im.getchannel("A")
    g = gris(im, 1.5, 2)
    linea = bordes(im, 2.0).filter(ImageFilter.GaussianBlur(0.4))
    relleno = ImageOps.invert(g).point(lambda v: int(v * 0.35))
    tiza = ImageChops.lighter(linea, relleno)
    tiza = ImageChops.multiply(tiza, grano(g.size, 26).point(lambda v: 140 + v // 3))
    color = duotono(tiza, (0, 0, 0), (244, 241, 232), (222, 226, 205))
    color.putalpha(ImageChops.multiply(a, tiza.point(lambda v: min(255, int(v * 1.6)))))
    return color


def neon(im: Image.Image) -> Image.Image:
    a = im.getchannel("A")
    g = gris(im, 1.7, 2)
    color = duotono(g, (24, 6, 46), (253, 244, 255), (255, 46, 151))
    brillo = color.filter(ImageFilter.GaussianBlur(14))
    color = ImageChops.screen(color, brillo)
    color.putalpha(a)
    return color


def billete(im: Image.Image) -> Image.Image:
    a = im.getchannel("A")
    g = gris(im, 1.5, 1)
    trama = lineas_grabado(g, paso=6, fuerza=0.92)
    color = duotono(trama, (18, 48, 36), (232, 240, 220), (52, 104, 78))
    color.putalpha(a)
    return color


def pop_art(im: Image.Image) -> Image.Image:
    a = im.getchannel("A")
    g = gris(im, 1.8, 3)
    color = posterizar_paleta(g, [(17, 17, 17), (227, 23, 45), (255, 217, 59), (255, 255, 255)])
    puntos = medios_tonos(g, paso=9).convert("RGB")
    color = ImageChops.multiply(color, ImageChops.lighter(puntos, Image.new("RGB", color.size, (120, 120, 120))))
    color.putalpha(a)
    return color


def andino(im: Image.Image) -> Image.Image:
    a = im.getchannel("A")
    g = gris(im, 1.4, 2)
    color = posterizar_paleta(g, [(58, 31, 20), (195, 52, 43), (227, 155, 45), (239, 223, 196)])
    tejido = grano(g.size, 10).convert("RGB")
    color = _mezclar(color, ImageChops.multiply(color, tejido.point(lambda v: 160 + v // 3)), 0.35)
    color.putalpha(a)
    return color


def plano(im: Image.Image) -> Image.Image:
    a = im.getchannel("A")
    g = gris(im, 1.5, 2)
    linea = bordes(im, 2.2)
    relleno = ImageOps.invert(g).point(lambda v: int(v * 0.30))
    trazo = ImageChops.lighter(linea, relleno)
    color = duotono(trazo, (10, 40, 78), (238, 246, 255), (143, 211, 255))
    color.putalpha(ImageChops.multiply(a, trazo.point(lambda v: min(255, int(v * 1.7)))))
    return color


def sellos_oficina(im: Image.Image) -> Image.Image:
    a = im.getchannel("A")
    g = gris(im, 2.2, 3)
    g = ImageChops.multiply(g, grano(g.size, 14).point(lambda v: 150 + v // 3))
    color = duotono(g, (28, 30, 38), (250, 247, 238), (120, 118, 118))
    color.putalpha(a)
    return color


def mapa_expedicion(im: Image.Image) -> Image.Image:
    a = im.getchannel("A")
    g = gris(im, 1.3, 2)
    color = duotono(g, (59, 39, 22), (245, 234, 208), (168, 120, 70))
    linea = bordes(im, 1.4).point(lambda v: 255 - v)
    color = ImageChops.multiply(color, linea.convert("RGB"))
    color = _mezclar(color, ImageChops.overlay(color, grano(g.size, 10).convert("RGB")), 0.25)
    color.putalpha(a)
    return color


RECETAS = {
    "vintage": vintage,
    "noir": noir,
    "pizarron": pizarron,
    "neon": neon,
    "billete": billete,
    "pop-art": pop_art,
    "andino": andino,
    "plano": plano,
    "sellos-oficina": sellos_oficina,
    "mapa-expedicion": mapa_expedicion,
}

ap = argparse.ArgumentParser()
ap.add_argument("foto")
ap.add_argument("slug")
ap.add_argument("--estilo", required=True)
ap.add_argument("--ya-recortada", action="store_true", help="la foto ya viene con fondo transparente")
ap.add_argument("--fundido", type=float, default=0.0, help="fracción inferior que se desvanece (0.15 típico)")
ap.add_argument("--alto", type=int, default=1500)
ap.add_argument("--sin-borde", action="store_true")
args = ap.parse_args()

if args.estilo not in ESTILOS:
    salir(f"Estilo desconocido: {args.estilo}. Hay: {', '.join(ESTILOS)}")
estilo = ESTILOS[args.estilo]
receta = RECETAS.get(estilo["foto"])
if receta is None:
    salir(f"El estilo {args.estilo} no tiene receta de foto.")
origen = pathlib.Path(args.foto)
if not origen.exists():
    salir(f"No encuentro la foto {origen}")
crear_carpetas()

im = Image.open(origen).convert("RGBA")
if not args.ya_recortada:
    try:
        from rembg import remove
    except ImportError:
        salir("Falta rembg (quita el fondo de la foto).  pip install rembg onnxruntime")
    print("Quitando el fondo (la primera vez descarga el modelo)…", flush=True)
    im = remove(im).convert("RGBA")

im = recortar_bbox(im)
im = receta(im)
if args.fundido > 0:
    im = fundido_abajo(im, args.fundido)
if not args.sin_borde:
    im = borde_sticker(im, estilo["recorte"]["borde"], estilo["recorte"]["grosorBorde"])
im = limitar_alto(im, args.alto)

destino = RECORTES / f"{args.slug}.png"
im.save(destino)
ok(f"{destino} · {im.size[0]}×{im.size[1]} · estilo {args.estilo}")
