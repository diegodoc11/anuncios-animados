"""Tiempos ESTIMADOS (sin gastar un solo crédito de voz).

Calcula cuánto va a durar cada beat y en qué frame cae cada palabra, para poder
montar y revisar el anuncio completo antes de generar la locución. Cuando después
generes la voz real, `transcribir_voz.py` reescribe estos mismos dos archivos con
los tiempos verdaderos y el anuncio se re-sincroniza solo.

Uso:  python -X utf8 pipeline/estimar_tiempos.py guiones/a1.json [--velocidad 14.5]
"""
from __future__ import annotations

import argparse
import json
import re

from comun import DATOS, FPS, cargar_guion, crear_carpetas, guardar_palabras, ok, perfil, texto_para_voz

ap = argparse.ArgumentParser()
ap.add_argument("guion")
ap.add_argument("--velocidad", type=float, default=14.5, help="caracteres por segundo (voz natural ≈ 14.5)")
ap.add_argument("--pad", type=int, default=5, help="frames de colchón al final de cada beat")
args = ap.parse_args()

guion = cargar_guion(args.guion)
crear_carpetas()
pron = {**(perfil().get("pronunciacion") or {}), **(guion.get("pronunciacion") or {})}

manifest = {"fps": FPS, "pad": args.pad, "estimado": True, "beats": []}
palabras_por_beat: dict[str, list] = {}

for beat in guion["beats"]:
    texto = texto_para_voz(beat["texto"], pron)
    piezas = [p for p in re.split(r"\s+", texto.strip()) if p]
    pesos = []
    for p in piezas:
        peso = len(p) + 1
        if re.search(r"[,;:]$", p):
            peso += 5
        if re.search(r"[.!?…]$", p):
            peso += 9
        pesos.append(peso)
    total = sum(pesos) or 1
    segundos = total / args.velocidad
    frames_beat = round(segundos * FPS) + args.pad

    acumulado = 0
    palabras = []
    for p, peso in zip(piezas, pesos):
        palabras.append([p, round(acumulado / args.velocidad * FPS)])
        acumulado += peso
    palabras_por_beat[beat["id"]] = palabras
    manifest["beats"].append({
        "id": beat["id"],
        "texto": beat["texto"],
        "frames": frames_beat,
        "segundos": round(segundos, 3),
    })

(DATOS / f"{guion['id']}.manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
guardar_palabras(DATOS / f"{guion['id']}.palabras.json", palabras_por_beat)

total_frames = sum(b["frames"] for b in manifest["beats"])
ok(f"Tiempos estimados de {guion['id']}: {len(manifest['beats'])} beats · {total_frames} frames ≈ {total_frames / FPS:.1f} s")
print("   (son estimados: la voz real manda. Genera la locución y corre transcribir_voz.py)")
