"""Guarda (y comprueba) las llaves, la voz y el perfil de marca de la skill.

Las llaves quedan en la carpeta personal del usuario, nunca dentro del proyecto.

Uso:
  python -X utf8 scripts/configurar.py estado
  python -X utf8 scripts/configurar.py llave KIE_API_KEY <valor>          (o por stdin: echo <valor> | ... llave KIE_API_KEY)
  python -X utf8 scripts/configurar.py llave ELEVENLABS_API_KEY <valor>
  python -X utf8 scripts/configurar.py voz <voice_id> "Nombre de la voz" [--modelo eleven_multilingual_v2]
  python -X utf8 scripts/configurar.py marca --negocio "Café La Esquina" --estilo vintage-50s --cta "Toca el botón"
  python -X utf8 scripts/configurar.py pronunciacion "Kie.ai" "Kaiei"
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

from config_comun import (ARCHIVO_LLAVES, ARCHIVO_PERFIL, DIR_CONFIG, guardar_llave, guardar_perfil,
                          leer_llaves, leer_perfil, ok, salir, tapada)


def comprobar_kie(valor: str) -> str:
    req = urllib.request.Request("https://api.kie.ai/api/v1/chat/credit",
                                 headers={"Authorization": f"Bearer {valor}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
        return f"créditos: {d.get('data')}"
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            salir("Kie.ai dice que esa llave no sirve. Cópiala otra vez desde kie.ai → API Key.")
        return "llave guardada (no pude leer el saldo)"
    except Exception:
        return "llave guardada (sin internet para comprobarla)"


def comprobar_elevenlabs(valor: str) -> str:
    req = urllib.request.Request("https://api.elevenlabs.io/v1/user/subscription",
                                 headers={"xi-api-key": valor})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
        restan = d.get("character_limit", 0) - d.get("character_count", 0)
        return f"plan {d.get('tier', '?')} · te quedan {restan} caracteres"
    except urllib.error.HTTPError as e:
        if e.code == 401:
            salir("ElevenLabs dice que esa llave no sirve. Cópiala otra vez desde elevenlabs.io → Profile → API key.")
        return "llave guardada (la llave no tiene permiso para leer el saldo, pero sirve para generar voz)"
    except Exception:
        return "llave guardada (sin internet para comprobarla)"


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="que", required=True)

sub.add_parser("estado")

p = sub.add_parser("llave")
p.add_argument("nombre", choices=["KIE_API_KEY", "ELEVENLABS_API_KEY"])
p.add_argument("valor", nargs="?", default="")

p = sub.add_parser("voz")
p.add_argument("voice_id")
p.add_argument("nombre", nargs="?", default="")
p.add_argument("--modelo", default="eleven_multilingual_v2")
p.add_argument("--estabilidad", type=float, default=0.45)
p.add_argument("--parecido", type=float, default=0.8)
p.add_argument("--estilo-voz", type=float, default=0.35)

p = sub.add_parser("marca")
p.add_argument("--negocio", default="")
p.add_argument("--instagram", default="")
p.add_argument("--estilo", default="")
p.add_argument("--cta", default="")
p.add_argument("--color", default="")
p.add_argument("--color-acento", default="")
p.add_argument("--carpeta-proyectos", default="")

p = sub.add_parser("pronunciacion")
p.add_argument("palabra")
p.add_argument("como_suena")

args = ap.parse_args()

if args.que == "estado":
    llaves = leer_llaves()
    perfil = leer_perfil()
    print(f"\nCarpeta de configuración: {DIR_CONFIG}")
    print(f"  KIE_API_KEY         {tapada(llaves.get('KIE_API_KEY', ''))}")
    print(f"  ELEVENLABS_API_KEY  {tapada(llaves.get('ELEVENLABS_API_KEY', ''))}")
    voz = perfil.get("voz") or {}
    print(f"  Voz                 {voz.get('nombre', '(sin elegir)')} {voz.get('id', '')}")
    print(f"  Negocio             {perfil.get('negocio', '(sin definir)')}")
    print(f"  Estilo por defecto  {perfil.get('estilo', '(sin definir)')}")
    print(f"  CTA por defecto     {perfil.get('cta', '(sin definir)')}")
    if perfil.get("pronunciacion"):
        print(f"  Pronunciación       {json.dumps(perfil['pronunciacion'], ensure_ascii=False)}")
    print(f"  Carpeta de proyectos {perfil.get('carpeta_proyectos', '(sin definir)')}")
    falta = [n for n in ("KIE_API_KEY", "ELEVENLABS_API_KEY") if not llaves.get(n)]
    print()
    if falta or not voz.get("id"):
        print("Falta por configurar: " + ", ".join(falta + ([] if voz.get("id") else ["la voz"])))
        sys.exit(2)
    ok("Configuración completa.")

elif args.que == "llave":
    valor = args.valor or sys.stdin.read().strip()
    if not valor:
        salir("No me llegó ningún valor para la llave.")
    detalle = comprobar_kie(valor) if args.nombre == "KIE_API_KEY" else comprobar_elevenlabs(valor)
    guardar_llave(args.nombre, valor)
    ok(f"{args.nombre} guardada en {ARCHIVO_LLAVES} · {detalle}")

elif args.que == "voz":
    perfil = leer_perfil()
    perfil["voz"] = {
        "id": args.voice_id,
        "nombre": args.nombre or args.voice_id,
        "modelo": args.modelo,
        "ajustes": {"stability": args.estabilidad, "similarity_boost": args.parecido,
                    "style": args.estilo_voz, "use_speaker_boost": True},
    }
    guardar_perfil(perfil)
    ok(f"Voz guardada: {perfil['voz']['nombre']} ({args.voice_id})")

elif args.que == "marca":
    perfil = leer_perfil()
    for clave, valor in (("negocio", args.negocio), ("instagram", args.instagram), ("estilo", args.estilo),
                         ("cta", args.cta), ("color", args.color), ("color_acento", args.color_acento),
                         ("carpeta_proyectos", args.carpeta_proyectos)):
        if valor:
            perfil[clave] = valor
    guardar_perfil(perfil)
    ok(f"Perfil guardado en {ARCHIVO_PERFIL}")

elif args.que == "pronunciacion":
    perfil = leer_perfil()
    perfil.setdefault("pronunciacion", {})[args.palabra] = args.como_suena
    guardar_perfil(perfil)
    ok(f'La voz dirá "{args.palabra}" como "{args.como_suena}"')
