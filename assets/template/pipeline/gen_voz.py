"""Locución con ElevenLabs, un clip por beat.

Trucos que hacen que suene humana y no a robot leyendo:
 · previous_text / next_text: el modelo "sabe" qué venía antes y qué viene después,
   así la entonación encadena entre beats en vez de reiniciarse en cada frase;
 · cifras escritas en palabras (11.200 → once mil doscientos);
 · diccionario de pronunciación para nombres de marca (perfil.json o el propio guion).

Los originales quedan en material/voz-original/ y NUNCA se tocan: apretar_voz.py
trabaja sobre copias.

Uso:
  python -X utf8 pipeline/gen_voz.py guiones/a1.json              # muestra qué haría y cuánto cuesta
  python -X utf8 pipeline/gen_voz.py guiones/a1.json --si         # genera de verdad
  python -X utf8 pipeline/gen_voz.py guiones/a1.json --si --solo a1-03,a1-07   # solo esos beats
"""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request

from comun import (VOZ_ORIGINAL, aviso, cargar_guion, crear_carpetas, llave, ok, perfil, salir,
                   texto_para_voz)

API = "https://api.elevenlabs.io/v1"

ap = argparse.ArgumentParser()
ap.add_argument("guion")
ap.add_argument("--si", action="store_true", help="confirma el gasto de créditos y genera")
ap.add_argument("--solo", default="", help="ids de beats separados por coma")
ap.add_argument("--voz", default="", help="voice_id (por defecto, el del perfil)")
ap.add_argument("--modelo", default="", help="por defecto eleven_multilingual_v2")
ap.add_argument("--rehacer", action="store_true", help="regenera aunque el clip ya exista")
args = ap.parse_args()

guion = cargar_guion(args.guion)
crear_carpetas()
p = perfil()
voz = args.voz or (p.get("voz") or {}).get("id", "")
if not voz:
    salir("No hay voz configurada. Corre la configuración de la skill (elegir voz) o pasa --voz <voice_id>.")
modelo = args.modelo or (p.get("voz") or {}).get("modelo") or "eleven_multilingual_v2"
ajustes = (p.get("voz") or {}).get("ajustes") or {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35,
                                                  "use_speaker_boost": True}
pron = {**(p.get("pronunciacion") or {}), **(guion.get("pronunciacion") or {})}
llave_el = llave("ELEVENLABS_API_KEY")
solo = [s.strip() for s in args.solo.split(",") if s.strip()]

# Texto real que se manda a la voz, beat por beat
textos = {b["id"]: texto_para_voz(b["texto"], pron) for b in guion["beats"]}
ids = [b["id"] for b in guion["beats"]]

pendientes = []
for i, b in enumerate(guion["beats"]):
    destino = VOZ_ORIGINAL / f"{b['id']}.mp3"
    firma = VOZ_ORIGINAL / f"{b['id']}.txt"
    igual = firma.exists() and firma.read_text(encoding="utf-8") == f"{voz}|{modelo}|{textos[b['id']]}"
    if solo and b["id"] not in solo:
        continue
    if destino.exists() and igual and not args.rehacer:
        continue
    pendientes.append((i, b))

if not pendientes:
    ok("La locución ya está completa y al día. Sigue con: pipeline/apretar_voz.py")
    raise SystemExit(0)

caracteres = sum(len(textos[b["id"]]) for _, b in pendientes)
print(f"\nVoz: {voz} · modelo: {modelo}")
print(f"Beats por generar: {len(pendientes)} · caracteres: {caracteres}\n")
for _, b in pendientes:
    print(f"  {b['id']}: {textos[b['id']]}")

# Saldo (si la llave tiene permiso de lectura de la cuenta)
try:
    req = urllib.request.Request(f"{API}/user/subscription", headers={"xi-api-key": llave_el})
    with urllib.request.urlopen(req, timeout=30) as r:
        sub = json.load(r)
    restan = sub.get("character_limit", 0) - sub.get("character_count", 0)
    print(f"\nCréditos disponibles en la cuenta: {restan}")
    if restan < caracteres:
        aviso("No alcanzan los créditos para todos los beats.")
except urllib.error.HTTPError:
    pass
except Exception:
    pass

if not args.si:
    print("\n(nada generado todavía) Repite el comando con --si para gastar créditos y generar.")
    raise SystemExit(0)

for i, b in pendientes:
    cuerpo = {
        "text": textos[b["id"]],
        "model_id": modelo,
        "voice_settings": ajustes,
    }
    if i > 0:
        cuerpo["previous_text"] = textos[ids[i - 1]]
    if i < len(ids) - 1:
        cuerpo["next_text"] = textos[ids[i + 1]]
    req = urllib.request.Request(
        f"{API}/text-to-speech/{voz}?output_format=mp3_44100_128",
        data=json.dumps(cuerpo).encode("utf-8"),
        headers={"xi-api-key": llave_el, "Content-Type": "application/json", "Accept": "audio/mpeg"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            audio = r.read()
    except urllib.error.HTTPError as e:
        salir(f"ElevenLabs respondió {e.code}: {e.read()[:400].decode('utf-8', 'replace')}")
    (VOZ_ORIGINAL / f"{b['id']}.mp3").write_bytes(audio)
    (VOZ_ORIGINAL / f"{b['id']}.txt").write_text(f"{voz}|{modelo}|{textos[b['id']]}", encoding="utf-8")
    print(f"  🎙️  {b['id']}.mp3 ({len(textos[b['id']])} caracteres)")

ok(f"Locución lista en {VOZ_ORIGINAL}")
print("Sigue con:  python -X utf8 pipeline/apretar_voz.py " + guion["_ruta"])
