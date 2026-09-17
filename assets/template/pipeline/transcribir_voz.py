"""Escucha la locución ya apretada y anota EN QUÉ FRAME suena cada palabra.

Sirve para dos cosas:
 1. verificar que la voz dijo exactamente lo que dice el guion (si se comió algo, avisa);
 2. dar los tiempos con los que el anuncio se sincroniza solo: en el código escribes
    en="pañal" y el gráfico entra en el frame en que se oye "pañal".

Usa faster-whisper en el computador (no cuesta créditos). La primera vez descarga
el modelo (~1.5 GB con "medium"); con --modelo small es más liviano y rápido.

Uso:  python -X utf8 pipeline/transcribir_voz.py guiones/a1.json [--modelo medium|small]
"""
from __future__ import annotations

import argparse
import difflib
import re

from comun import (DATOS, FPS, VOZ, aviso, cargar_guion, cifras_a_palabras, crear_carpetas,
                   guardar_palabras, normalizar, ok, perfil, salir, texto_para_voz)

ap = argparse.ArgumentParser()
ap.add_argument("guion")
ap.add_argument("--modelo", default="medium", choices=["tiny", "base", "small", "medium", "large-v3"])
ap.add_argument("--idioma", default="es")
args = ap.parse_args()

try:
    from faster_whisper import WhisperModel
except ImportError:
    salir("Falta faster-whisper.  pip install faster-whisper")

guion = cargar_guion(args.guion)
crear_carpetas()
pron = {**(perfil().get("pronunciacion") or {}), **(guion.get("pronunciacion") or {})}
print(f"Cargando el modelo {args.modelo} (la primera vez se descarga)…", flush=True)
modelo = WhisperModel(args.modelo, device="cpu", compute_type="int8")

palabras_por_beat: dict[str, list] = {}
problemas = []

for b in guion["beats"]:
    clip = VOZ / f"{b['id']}.mp3"
    if not clip.exists():
        salir(f"Falta {clip}. Corre antes pipeline/apretar_voz.py")
    segmentos, _ = modelo.transcribe(str(clip), language=args.idioma, word_timestamps=True, beam_size=5)

    palabras = []
    for s in segmentos:
        for w in s.words or []:
            crudo = w.word.strip()
            # Whisper escribe los números con cifras ("58"): los pasamos a palabras
            # para que coincidan con el guion y se puedan usar como ancla.
            texto = cifras_a_palabras(crudo)
            trozos = [t for t in texto.split() if t]
            if len(trozos) <= 1:
                palabras.append([trozos[0] if trozos else crudo, round(w.start * FPS)])
            else:
                dur = max(0.0, w.end - w.start)
                for k, t in enumerate(trozos):
                    palabras.append([t, round((w.start + dur * k / len(trozos)) * FPS)])
    palabras_por_beat[b["id"]] = palabras

    oido = " ".join(p for p, _ in palabras)
    guion_voz = texto_para_voz(b["texto"], pron)
    a = [normalizar(x) for x in re.split(r"\s+", guion_voz) if normalizar(x)]
    c = [normalizar(p) for p, _ in palabras]
    iguales = difflib.SequenceMatcher(a=a, b=c, autojunk=False).ratio()
    print(f"\n{b['id']}  ({iguales * 100:.0f}% igual al guion)")
    print(f"  guion: {guion_voz}")
    print(f"  oído : {oido}")
    print("  frames: " + " ".join(f"{p}@{f}" for p, f in palabras))
    if iguales < 0.93:
        faltan = [x for x in a if x not in c]
        problemas.append((b["id"], faltan))

guardar_palabras(DATOS / f"{guion['id']}.palabras.json", palabras_por_beat)

print()
if problemas:
    aviso("Estos beats no se oyeron igual que el guion:")
    for bid, faltan in problemas:
        print(f"   {bid}: no se oyeron → {', '.join(faltan[:8]) or '(orden distinto)'}")
    print("   Arréglalo así: baja el tempo de ese beat en el guion (\"tempo\": 1.0) y vuelve a correr")
    print("   apretar_voz.py, o regenera la voz de ese beat:  gen_voz.py <guion> --si --solo <beat> --rehacer")
else:
    ok("La voz dice exactamente lo que dice el guion.")
ok(f"Tiempos por palabra guardados en src/data/{guion['id']}.palabras.json")
