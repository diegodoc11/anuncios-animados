"""Aprieta el ritmo de la locución (lo que separa un anuncio que retiene de uno que aburre).

Sobre cada clip original:
 1. recorta el silencio del arranque y del final,
 2. acorta las pausas internas largas,
 3. acelera un poquito sin cambiar el tono (atempo, por defecto 1.1).

Los originales de material/voz-original/ NO se tocan; el resultado va a public/voz/
y los tiempos de cada beat quedan en src/data/<anuncio>.manifest.json.

Uso:  python -X utf8 pipeline/apretar_voz.py guiones/a1.json [--tempo 1.1] [--pausa 0] [--pad 5] [--cola 25]
  --pausa  silencio que se deja en cada pausa interna (0 ya deja una pausa natural corta)
  --pad    frames de colchón al final de cada beat
  --cola   frames extra al final del ÚLTIMO beat (para que el CTA respire)
Si un beat se come una palabra al acelerar, ponle "tempo": 1.0 a ese beat en el guion.
"""
from __future__ import annotations

import argparse
import json

from comun import DATOS, FPS, VOZ, VOZ_ORIGINAL, cargar_guion, correr, crear_carpetas, duracion, ok, salir

ap = argparse.ArgumentParser()
ap.add_argument("guion")
ap.add_argument("--tempo", type=float, default=1.1)
ap.add_argument("--pausa", type=float, default=0.0)
ap.add_argument("--pad", type=int, default=5)
ap.add_argument("--cola", type=int, default=25)
args = ap.parse_args()

guion = cargar_guion(args.guion)
crear_carpetas()


def filtro(tempo: float) -> str:
    return (f"silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02:"
            f"stop_periods=-1:stop_duration=0.2:stop_threshold=-45dB:stop_silence={args.pausa}:detection=rms,"
            f"atempo={tempo}")


beats = []
antes = despues = 0.0
for n, b in enumerate(guion["beats"], 1):
    origen = VOZ_ORIGINAL / f"{b['id']}.mp3"
    if not origen.exists():
        salir(f"Falta el clip {origen}. Genera la voz primero (pipeline/gen_voz.py).")
    destino = VOZ / f"{b['id']}.mp3"
    correr(["ffmpeg", "-v", "error", "-y", "-i", str(origen), "-af", filtro(float(b.get("tempo", args.tempo))),
            "-c:a", "libmp3lame", "-b:a", "192k", str(destino)])
    d0, d1 = duracion(origen), duracion(destino)
    antes += d0
    despues += d1
    extra = args.pad + (args.cola if n == len(guion["beats"]) else 0)
    beats.append({
        "id": b["id"],
        "texto": b["texto"],
        "frames": round(d1 * FPS) + extra,
        "segundos": round(d1, 3),
        "voz": f"voz/{b['id']}.mp3",
    })
    print(f"  {b['id']}: {d0:.2f}s → {d1:.2f}s")

manifest = {"fps": FPS, "pad": args.pad, "tempo": args.tempo, "estimado": False, "beats": beats}
(DATOS / f"{guion['id']}.manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
total = sum(b["frames"] for b in beats)
ok(f"Voz apretada: {antes:.1f}s → {despues:.1f}s · video ≈ {total / FPS:.1f}s")
print("Sigue con:  python -X utf8 pipeline/transcribir_voz.py " + guion["_ruta"])
