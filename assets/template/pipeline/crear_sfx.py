"""Crea los efectos de sonido del proyecto con ffmpeg (síntesis pura).

No se descarga ni se copia audio de nadie: cada .wav se genera con una fórmula,
así que son tuyos y puedes usarlos en anuncios de clientes sin problema.

Uso:  python -X utf8 pipeline/crear_sfx.py [--rehacer]
Salida: public/sfx/whoosh.wav, pop.wav, click.wav, golpe.wav, papel.wav, ding.wav
"""
from __future__ import annotations

import argparse

from comun import SFX, correr, crear_carpetas, hay, ok, salir

# Cada efecto: (filtro de fuente, filtros extra)
RECETAS = {
    # deslizamiento: ruido con barrido de graves a agudos
    "whoosh": (
        "aevalsrc='(random(0)*2-1)*0.9:d=0.55:s=48000'",
        "highpass=f=250,lowpass=f=5200,"
        "volume='min(1,t*7)*exp(-4.5*max(0,t-0.14))':eval=frame,"
        "aformat=channel_layouts=mono,volume=0.9",
    ),
    # entrada de un objeto: burbuja corta que baja de tono
    "pop": (
        "aevalsrc='sin(2*PI*t*(820-2300*t))*exp(-24*t):d=0.2:s=48000'",
        "volume=0.9,aformat=channel_layouts=mono",
    ),
    # tic seco para etiquetas pequeñas
    "click": (
        "aevalsrc='(random(1)*2-1)*exp(-150*t):d=0.08:s=48000'",
        "highpass=f=800,volume=0.8,aformat=channel_layouts=mono",
    ),
    # sello de caucho contra la mesa
    "golpe": (
        "aevalsrc='(sin(2*PI*95*t)*0.85+(random(2)*2-1)*0.55)*exp(-15*t):d=0.4:s=48000'",
        "lowpass=f=3000,volume=1.0,aformat=channel_layouts=mono",
    ),
    # hoja de papel que se desliza
    "papel": (
        "aevalsrc='(random(3)*2-1)*0.7:d=0.4:s=48000'",
        "bandpass=f=2600:width_type=o:w=2.2,"
        "volume='min(1,t*12)*exp(-7*max(0,t-0.1))':eval=frame,"
        "volume=1.4,aformat=channel_layouts=mono",
    ),
    # campanita para el remate / CTA
    "ding": (
        "aevalsrc='(sin(2*PI*1568*t)+0.45*sin(2*PI*3136*t))*exp(-4.5*t)*0.5:d=1.2:s=48000'",
        "volume=0.8,aformat=channel_layouts=mono",
    ),
}

ap = argparse.ArgumentParser()
ap.add_argument("--rehacer", action="store_true", help="vuelve a crear los que ya existen")
args = ap.parse_args()

if not hay("ffmpeg"):
    salir("Falta ffmpeg. Instálalo y vuelve a correr este script.")

crear_carpetas()
for nombre, (fuente, filtros) in RECETAS.items():
    destino = SFX / f"{nombre}.wav"
    if destino.exists() and not args.rehacer:
        print(f"  ya estaba: {destino.name}")
        continue
    correr(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", fuente, "-af", filtros,
            "-c:a", "pcm_s16le", "-ar", "48000", str(destino)])
    print(f"  creado: {destino.name}")

ok(f"Efectos de sonido listos en {SFX}")
