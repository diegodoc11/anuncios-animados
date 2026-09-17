"""Configuración compartida de la skill: dónde viven las llaves y el perfil.

Las llaves NUNCA se guardan dentro del repositorio ni dentro de un proyecto:
van a la carpeta personal del usuario.
  Windows:  C:\\Users\\<tu usuario>\\.config\\anuncios-animados\\
  macOS/Linux:  ~/.config/anuncios-animados/
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

DIR_CONFIG = pathlib.Path(os.environ.get(
    "ANUNCIOS_ANIMADOS_CONFIG", pathlib.Path.home() / ".config" / "anuncios-animados"))
ARCHIVO_LLAVES = DIR_CONFIG / "llaves.env"
ARCHIVO_PERFIL = DIR_CONFIG / "perfil.json"
CASTING = DIR_CONFIG / "casting"


def leer_llaves() -> dict:
    datos = {}
    if ARCHIVO_LLAVES.exists():
        for linea in ARCHIVO_LLAVES.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                k, v = linea.split("=", 1)
                datos[k.strip()] = v.strip()
    return datos


def guardar_llave(nombre: str, valor: str) -> None:
    DIR_CONFIG.mkdir(parents=True, exist_ok=True)
    datos = leer_llaves()
    datos[nombre] = valor.strip()
    ARCHIVO_LLAVES.write_text(
        "# Llaves de la skill anuncios-animados. NO subir esto a ningún repositorio.\n"
        + "\n".join(f"{k}={v}" for k, v in datos.items()) + "\n",
        encoding="utf-8")
    try:
        os.chmod(ARCHIVO_LLAVES, 0o600)
    except OSError:
        pass


def llave(nombre: str) -> str:
    # Manda lo que guardó la configuración; la variable de entorno es solo el respaldo
    # (suele haber variables viejas de otras herramientas que ya no sirven).
    valor = leer_llaves().get(nombre, "") or os.environ.get(nombre, "")
    if valor and nombre == "ELEVENLABS_API_KEY" and not valor.startswith("sk_"):
        print("⚠️  Esa llave de ElevenLabs no parece una llave: las buenas empiezan por 'sk_'.")
    return valor


def leer_perfil() -> dict:
    if ARCHIVO_PERFIL.exists():
        return json.loads(ARCHIVO_PERFIL.read_text(encoding="utf-8"))
    return {}


def guardar_perfil(perfil: dict) -> None:
    DIR_CONFIG.mkdir(parents=True, exist_ok=True)
    ARCHIVO_PERFIL.write_text(json.dumps(perfil, ensure_ascii=False, indent=2), encoding="utf-8")


def tapada(valor: str) -> str:
    """Muestra una llave sin revelarla: sk_1234…ab90"""
    if not valor:
        return "(sin configurar)"
    return valor[:6] + "…" + valor[-4:] if len(valor) > 12 else "(configurada)"


def salir(mensaje: str) -> None:
    print(f"\n❌ {mensaje}\n", flush=True)
    sys.exit(1)


def ok(mensaje: str) -> None:
    print(f"✅ {mensaje}", flush=True)
