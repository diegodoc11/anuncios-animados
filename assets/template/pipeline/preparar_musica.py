"""Deja la música a la altura exacta: colchón por debajo de la voz, con entrada y salida suaves.

Mide cuán fuerte quedó la locución, mide la música y le baja (o sube) el volumen para que
quede unos 15 dB por debajo. Así se siente sin tapar ni una palabra. También la recorta al
largo del anuncio y le hace fundido de entrada y de salida.

Uso:
  python -X utf8 pipeline/preparar_musica.py guiones/a1.json material/musica-original/a1-1.mp3 [--debajo 15]

Salida: public/musica/<anuncio>.mp3  →  en el anuncio:  musica: { src: "musica/a1.mp3" }
"""
from __future__ import annotations

import argparse
import json
import pathlib
import tempfile

from comun import DATOS, FPS, MUSICA, VOZ, aviso, cargar_guion, correr, crear_carpetas, loudness, ok, salir

ap = argparse.ArgumentParser()
ap.add_argument("guion")
ap.add_argument("musica")
ap.add_argument("--debajo", type=float, default=15.0, help="dB por debajo de la voz")
ap.add_argument("--entrada", type=float, default=1.0, help="segundos de fundido de entrada")
ap.add_argument("--salida", type=float, default=2.0, help="segundos de fundido de salida")
args = ap.parse_args()

guion = cargar_guion(args.guion)
crear_carpetas()
pista = pathlib.Path(args.musica)
if not pista.exists():
    salir(f"No encuentro la música {pista}")

ruta_manifest = DATOS / f"{guion['id']}.manifest.json"
if not ruta_manifest.exists():
    salir(f"Falta {ruta_manifest}. Corre antes apretar_voz.py (o estimar_tiempos.py).")
manifest = json.loads(ruta_manifest.read_text(encoding="utf-8"))
segundos = sum(b["frames"] for b in manifest["beats"]) / FPS

clips = [VOZ / f"{b['id']}.mp3" for b in manifest["beats"] if (VOZ / f"{b['id']}.mp3").exists()]
if clips:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{c.as_posix()}'\n")
        lista = f.name
    with tempfile.TemporaryDirectory() as tmp:
        junta = pathlib.Path(tmp) / "voz.mp3"
        correr(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", str(junta)])
        nivel_voz = loudness(junta)
    pathlib.Path(lista).unlink(missing_ok=True)
else:
    aviso("Todavía no hay voz: uso -20 LUFS como referencia.")
    nivel_voz = -20.0

nivel_musica = loudness(pista)
objetivo = nivel_voz - args.debajo
ganancia = objetivo - nivel_musica
destino = MUSICA / f"{guion['id']}.mp3"

correr(["ffmpeg", "-v", "error", "-y", "-i", str(pista),
        "-af", (f"volume={ganancia:.2f}dB,"
                f"afade=t=in:st=0:d={args.entrada},"
                f"afade=t=out:st={max(0.1, segundos - args.salida):.2f}:d={args.salida}"),
        "-t", f"{segundos:.2f}", "-c:a", "libmp3lame", "-b:a", "192k", str(destino)])

ok(f"{destino.name} · voz {nivel_voz:.1f} LUFS · música {nivel_musica:.1f} → {objetivo:.1f} LUFS "
   f"({ganancia:+.1f} dB) · {segundos:.1f}s")
print(f'En el anuncio:  musica: {{ src: "musica/{guion["id"]}.mp3" }}')
