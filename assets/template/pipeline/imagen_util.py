"""Utilidades de imagen que comparten recortar.py y foto_real.py."""
from __future__ import annotations

import random

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps


def recortar_bbox(im: Image.Image, margen: int = 6) -> Image.Image:
    caja = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if not caja:
        return im
    w, h = im.size
    return im.crop((max(0, caja[0] - margen), max(0, caja[1] - margen),
                    min(w, caja[2] + margen), min(h, caja[3] + margen)))


def borde_sticker(im: Image.Image, color: str, grosor: int) -> Image.Image:
    """Contorno de color alrededor del recorte (como una calcomanía)."""
    if grosor <= 0 or not color:
        return im
    lienzo = Image.new("RGBA", (im.width + 2 * grosor, im.height + 2 * grosor), (0, 0, 0, 0))
    base = Image.new("L", lienzo.size, 0)
    base.paste(im.getchannel("A").point(lambda v: 255 if v > 40 else 0), (grosor, grosor))
    crecido = base
    for _ in range(max(1, grosor // 2)):
        crecido = crecido.filter(ImageFilter.MaxFilter(5))
    crecido = crecido.filter(ImageFilter.GaussianBlur(1.5)).point(lambda v: 255 if v > 100 else 0)
    lienzo.paste(Image.new("RGBA", lienzo.size, color), (0, 0), crecido)
    lienzo.alpha_composite(im, (grosor, grosor))
    return lienzo


def limitar_alto(im: Image.Image, alto: int) -> Image.Image:
    if im.height <= alto:
        return im
    escala = alto / im.height
    return im.resize((max(1, int(im.width * escala)), alto), Image.LANCZOS)


def fundido_abajo(im: Image.Image, fraccion: float) -> Image.Image:
    """Desvanece el borde inferior (cuando la foto queda cortada a la altura de las rodillas)."""
    if fraccion <= 0:
        return im
    w, h = im.size
    alto = max(1, int(h * fraccion))
    degradado = Image.linear_gradient("L").resize((w, alto))
    mascara = Image.new("L", (w, h), 255)
    mascara.paste(ImageOps.invert(degradado), (0, h - alto))
    im.putalpha(ImageChops.multiply(im.getchannel("A"), mascara))
    return im


def grano(size, amplitud: int = 16, semilla: int = 7) -> Image.Image:
    random.seed(semilla)
    return Image.effect_noise(size, amplitud).convert("L")


def gris(im: Image.Image, contraste: float = 1.4, recorte: int = 2) -> Image.Image:
    g = ImageOps.grayscale(im.convert("RGB"))
    g = ImageOps.autocontrast(g, cutoff=recorte)
    return ImageEnhance.Contrast(g).enhance(contraste)


def duotono(g: Image.Image, oscuro, claro, medio=None) -> Image.Image:
    return ImageOps.colorize(g, black=oscuro, white=claro, mid=medio)


def persiana(size, ancho: int = 46, hueco: int = 58, angulo: int = -18, fuerza: float = 0.42) -> Image.Image:
    """Sombras de persiana en diagonal (cine negro)."""
    from PIL import ImageDraw

    w, h = size
    grande = int((w ** 2 + h ** 2) ** 0.5) + 10
    m = Image.new("L", (grande, grande), 255)
    d = ImageDraw.Draw(m)
    y = 0
    while y < grande:
        d.rectangle([0, y, grande, y + ancho], fill=int(255 * (1 - fuerza)))
        y += ancho + hueco
    m = m.filter(ImageFilter.GaussianBlur(10)).rotate(angulo, resample=Image.BICUBIC)
    izq, arr = (grande - w) // 2, (grande - h) // 2
    return m.crop((izq, arr, izq + w, arr + h))


def lineas_grabado(g: Image.Image, paso: int = 6, fuerza: float = 0.9) -> Image.Image:
    """Trama de líneas horizontales cuyo grosor depende del tono (grabado de billete)."""
    import math

    w, h = g.size
    patron = Image.new("L", (w, h), 255)
    px = patron.load()
    gp = g.load()
    for y in range(h):
        onda = (math.sin(y / paso * math.pi) + 1) / 2  # 0..1
        for x in range(0, w, 1):
            tono = gp[x, y] / 255
            px[x, y] = 255 if onda < tono ** 1.3 else int(255 * (1 - fuerza))
    return patron


def medios_tonos(g: Image.Image, paso: int = 9) -> Image.Image:
    """Puntos tipo cómic: más grandes donde la imagen es oscura."""
    from PIL import ImageDraw

    w, h = g.size
    capa = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(capa)
    gp = g.load()
    for y in range(0, h, paso):
        for x in range(0, w, paso):
            tono = gp[min(x, w - 1), min(y, h - 1)] / 255
            r = (1 - tono) * paso * 0.62
            if r > 0.4:
                d.ellipse([x - r, y - r, x + r, y + r], fill=0)
    return capa


def bordes(im: Image.Image, fuerza: float = 1.6) -> Image.Image:
    """Mapa de líneas (0 = nada, 255 = línea fuerte)."""
    g = ImageOps.grayscale(im.convert("RGB"))
    suave = g.filter(ImageFilter.GaussianBlur(1.2))
    mas_suave = g.filter(ImageFilter.GaussianBlur(3.2))
    dif = ImageChops.difference(suave, mas_suave)
    dif = ImageOps.autocontrast(dif, cutoff=1)
    return ImageEnhance.Brightness(dif).enhance(fuerza)


def posterizar_paleta(g: Image.Image, colores: list[tuple[int, int, int]]) -> Image.Image:
    """Mapea los tonos a una paleta fija (del más oscuro al más claro)."""
    n = len(colores)
    tabla = []
    for canal in range(3):
        tabla += [colores[min(n - 1, int(v / 256 * n))][canal] for v in range(256)]
    return g.convert("RGB").point(tabla)
