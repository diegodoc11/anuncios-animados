"""Crea la carpeta de trabajo de un cliente/marca a partir de la plantilla.

Un proyecto = una marca. Dentro puedes tener muchos anuncios (a1, a2, a3…) que comparten
personajes, escenografía, música y estilo.

Uso:
  python -X utf8 scripts/nuevo_proyecto.py "C:\\Users\\tu-usuario\\Documents\\Anuncios\\Cafe La Esquina"
  python -X utf8 scripts/nuevo_proyecto.py ~/Anuncios/cliente --sin-npm
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

from config_comun import ok, salir

SKILL = pathlib.Path(__file__).resolve().parent.parent
PLANTILLA = SKILL / "assets" / "template"

NO_COPIAR = shutil.ignore_patterns("node_modules", "out", "material", ".remotion", "*.mp4", "*.mp3",
                                   "*.wav", "revision", "__pycache__")

ap = argparse.ArgumentParser()
ap.add_argument("carpeta")
ap.add_argument("--sin-npm", action="store_true", help="no instalar las dependencias todavía")
args = ap.parse_args()

destino = pathlib.Path(args.carpeta).expanduser()
if destino.exists() and any(destino.iterdir()):
    salir(f"La carpeta {destino} ya existe y tiene cosas adentro. Usa otra o bórrala.")
if not PLANTILLA.exists():
    salir(f"No encuentro la plantilla en {PLANTILLA}")

shutil.copytree(PLANTILLA, destino, ignore=NO_COPIAR)
for carpeta in ("material/voz-original", "material/imagenes-originales", "material/musica-original",
                "material/fotos", "public/voz", "public/recortes", "public/escenografia",
                "public/musica", "public/sfx", "out"):
    (destino / carpeta).mkdir(parents=True, exist_ok=True)
ok(f"Proyecto creado en {destino}")

if not args.sin_npm:
    print("\nInstalando Remotion (tarda 1–3 minutos la primera vez)…", flush=True)
    r = subprocess.run(["npm", "install", "--no-audit", "--no-fund"], cwd=destino, shell=(sys.platform == "win32"))
    if r.returncode != 0:
        salir("Falló npm install. Revisa que Node.js 18+ esté instalado.")
    ok("Remotion instalado")

print("\nCreando los efectos de sonido…", flush=True)
subprocess.run([sys.executable, "-X", "utf8", str(destino / "pipeline" / "crear_sfx.py")], cwd=destino)

print(f"""
Listo. Siguiente paso, dentro de {destino}:
  1. guiones/<anuncio>.json   ← el guion por beats
  2. python -X utf8 pipeline/estimar_tiempos.py guiones/<anuncio>.json
  3. python -X utf8 pipeline/esqueleto_anuncio.py <anuncio>
  4. npx remotion studio       ← para ver el anuncio mientras lo armas
""")
