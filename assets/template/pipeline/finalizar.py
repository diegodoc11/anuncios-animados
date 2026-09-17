"""Remate del video ya renderizado: volumen parejo para redes + copia liviana para el celular.

 1. Normaliza el audio a -14 LUFS con pico máximo -1 dBTP (el estándar que usan
    Instagram, TikTok y YouTube: así no te suben ni te bajan el volumen).
 2. Saca una copia comprimida de menos de 30 MB para mandar por WhatsApp o revisar en el celular.

Uso:  python -X utf8 pipeline/finalizar.py out/a1.mp4 [--limite 28]
Salida: out/a1-final.mp4  y  out/a1-celular.mp4
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess

from comun import correr, duracion, ok, salir

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("--limite", type=float, default=28.0, help="MB máximos de la copia de celular")
ap.add_argument("--lufs", type=float, default=-14.0)
args = ap.parse_args()

video = pathlib.Path(args.video)
if not video.exists():
    salir(f"No encuentro {video}")

# ── 1. medir el audio ───────────────────────────────────────────────────────────
medicion = subprocess.run(
    ["ffmpeg", "-v", "info", "-i", str(video), "-af",
     f"loudnorm=I={args.lufs}:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
    capture_output=True, text=True, encoding="utf-8", errors="replace")
bloques = re.findall(r"\{[^{}]*input_i[^{}]*\}", medicion.stderr, re.S)
if not bloques:
    salir("No pude medir el audio del video (¿tiene pista de audio?).")
m = json.loads(bloques[-1])
print(f"  audio original: {float(m['input_i']):.1f} LUFS · pico {float(m['input_tp']):.1f} dBTP")

final = video.with_name(video.stem + "-final.mp4")
correr(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-af",
        (f"loudnorm=I={args.lufs}:TP=-1:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
         f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(final)])
ok(f"{final.name} · audio a {args.lufs} LUFS")

# ── 2. copia liviana ────────────────────────────────────────────────────────────
segundos = duracion(final)
celular = video.with_name(video.stem + "-celular.mp4")
objetivo = args.limite
for intento in range(3):
    total_kbps = objetivo * 8 * 1024 / segundos           # kbit/s para todo el archivo
    video_kbps = max(600, int(total_kbps - 128))
    correr(["ffmpeg", "-v", "error", "-y", "-i", str(final),
            "-c:v", "libx264", "-preset", "medium", "-crf", "24",
            "-maxrate", f"{video_kbps}k", "-bufsize", f"{video_kbps * 2}k",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(celular)])
    mb = celular.stat().st_size / 1024 / 1024
    if mb <= 30:
        ok(f"{celular.name} · {mb:.1f} MB · {segundos:.1f}s")
        break
    objetivo *= 0.8
else:
    salir("No logré bajar de 30 MB: acorta el anuncio o baja la resolución.")

print(f"\nListo para subir:  {final}")
