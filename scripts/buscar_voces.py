"""Casting de voz: busca voces en la biblioteca pública de ElevenLabs y, si quieres,
hace que todas digan LA MISMA frase para que puedas comparar peras con peras.

Escuchar las muestras de la biblioteca (preview_url) no cuesta créditos.
Generar la frase propia sí cuesta: se avisa cuántos caracteres antes de gastar.

Uso:
  python -X utf8 scripts/buscar_voces.py --idioma es --acento colombian --genero female
  python -X utf8 scripts/buscar_voces.py --idioma es --genero male --n 6 --generar --si \
         --frase "Así va a sonar tu anuncio, con esta voz."
"""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request

from config_comun import CASTING, llave, ok, salir

API = "https://api.elevenlabs.io/v1"

ap = argparse.ArgumentParser()
ap.add_argument("--idioma", default="es")
ap.add_argument("--acento", default="", help="colombian, mexican, argentinian, castilian, latin america…")
ap.add_argument("--genero", default="", choices=["", "female", "male", "neutral"])
ap.add_argument("--edad", default="", choices=["", "young", "middle_aged", "old"])
ap.add_argument("--buscar", default="", help="palabras sueltas: warm, narration, energetic…")
ap.add_argument("--n", type=int, default=6, help="cuántas candidatas mostrar")
ap.add_argument("--frase", default="Así va a sonar tu anuncio. Mira el video y agenda hoy mismo.")
ap.add_argument("--generar", action="store_true", help="genera la misma frase con cada candidata")
ap.add_argument("--si", action="store_true", help="confirma el gasto de créditos")
ap.add_argument("--modelo", default="eleven_multilingual_v2")
args = ap.parse_args()

api_key = llave("ELEVENLABS_API_KEY")
if not api_key:
    salir("Falta ELEVENLABS_API_KEY. Guárdala con scripts/configurar.py llave ELEVENLABS_API_KEY <valor>")

parametros = {"page_size": 60, "language": args.idioma}
if args.genero:
    parametros["gender"] = args.genero
if args.edad:
    parametros["age"] = args.edad
if args.buscar:
    parametros["search"] = args.buscar
url = f"{API}/shared-voices?" + urllib.parse.urlencode(parametros)
req = urllib.request.Request(url, headers={"xi-api-key": api_key})
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        datos = json.load(r)
except urllib.error.HTTPError as e:
    salir(f"ElevenLabs respondió {e.code}: {e.read()[:300].decode('utf-8', 'replace')}")

voces = datos.get("voices") or []
if args.acento:
    filtradas = [v for v in voces if args.acento.lower() in (v.get("accent") or "").lower()]
    voces = filtradas or voces
    if not filtradas:
        print(f"(no había voces con acento «{args.acento}»: te muestro las demás del idioma)")
voces = voces[: args.n]
if not voces:
    salir("No encontré voces con esos filtros. Prueba sin --acento o con otro idioma.")

print(f"\n{len(voces)} voces candidatas ({args.idioma}{' · ' + args.acento if args.acento else ''}):\n")
for i, v in enumerate(voces, 1):
    print(f"{i}. {v.get('name')}  [{v.get('voice_id')}]")
    print(f"   acento: {v.get('accent', '?')} · edad: {v.get('age', '?')} · uso: {v.get('use_case', '?')}")
    if v.get("description"):
        print(f"   {v['description'][:110]}")
    print(f"   muestra gratis: {v.get('preview_url')}\n")

if not args.generar:
    print("Escucha las muestras de arriba (no cuestan créditos).")
    print("Para oírlas todas diciendo TU frase, repite con:  --generar --si")
    raise SystemExit(0)

costo = len(args.frase) * len(voces)
print(f"Generar «{args.frase}» con {len(voces)} voces cuesta ≈ {costo} caracteres.")
if not args.si:
    print("(no se generó nada) Agrega --si para confirmar.")
    raise SystemExit(0)

CASTING.mkdir(parents=True, exist_ok=True)
for i, v in enumerate(voces, 1):
    cuerpo = {"text": args.frase, "model_id": args.modelo}
    req = urllib.request.Request(
        f"{API}/text-to-speech/{v['voice_id']}?output_format=mp3_44100_128",
        data=json.dumps(cuerpo).encode("utf-8"),
        headers={"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            audio = r.read()
    except urllib.error.HTTPError as e:
        detalle = e.read()[:300].decode("utf-8", "replace")
        print(f"   ⚠️  {v.get('name')}: no pude generar ({e.code}). {detalle}")
        continue
    nombre = f"{i:02d}-{v.get('name', 'voz').replace(' ', '-')}-{v['voice_id']}.mp3"
    (CASTING / nombre).write_bytes(audio)
    print(f"   🎧 {nombre}")

ok(f"Muestras en {CASTING}")
print("Escúchalas, elige una y guárdala con:")
print('  python -X utf8 scripts/configurar.py voz <voice_id> "<nombre>"')
