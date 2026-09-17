"""Revisa que el computador tenga todo lo necesario y dice exactamente qué instalar.

Uso:  python -X utf8 scripts/revisar_dependencias.py
"""
from __future__ import annotations

import importlib
import platform
import re
import shutil
import subprocess
import sys

SO = platform.system()  # Windows | Darwin | Linux


def version_de(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr).strip().splitlines()[0]
    except Exception:
        return ""


def como_instalar(que: str) -> str:
    recetas = {
        "node": {"Windows": "winget install OpenJS.NodeJS.LTS", "Darwin": "brew install node",
                 "Linux": "sudo apt install nodejs npm"},
        "ffmpeg": {"Windows": "winget install Gyan.FFmpeg", "Darwin": "brew install ffmpeg",
                   "Linux": "sudo apt install ffmpeg"},
        "python": {"Windows": "winget install Python.Python.3.12", "Darwin": "brew install python@3.12",
                   "Linux": "sudo apt install python3 python3-pip"},
    }
    return recetas.get(que, {}).get(SO, "")


filas = []
falta_algo = False

# Node 18+
nodo = version_de(["node", "--version"])
mayor = int(re.sub(r"[^0-9.].*", "", nodo.lstrip("v")).split(".")[0]) if nodo else 0
bien = mayor >= 18
filas.append(("Node.js 18 o más", nodo or "no está", bien, como_instalar("node")))
falta_algo |= not bien

# npm
npm = version_de(["npm", "--version"]) if shutil.which("npm") else ""
filas.append(("npm", npm or "no está", bool(npm), como_instalar("node")))
falta_algo |= not npm

# ffmpeg / ffprobe
for prog in ("ffmpeg", "ffprobe"):
    v = version_de([prog, "-version"])
    filas.append((prog, v[:48] if v else "no está", bool(v), como_instalar("ffmpeg")))
    falta_algo |= not v

# Python 3.9+
filas.append((f"Python {platform.python_version()}", sys.executable, sys.version_info >= (3, 9), como_instalar("python")))

# Paquetes de Python
paquetes = {
    "PIL": ("Pillow (dibujar hojas de contacto y estilizar fotos)", "pip install Pillow"),
    "numpy": ("numpy (recorte por chroma)", "pip install numpy"),
    "faster_whisper": ("faster-whisper (tiempos por palabra)", "pip install faster-whisper"),
    "rembg": ("rembg (quitar el fondo de fotos reales)", "pip install rembg onnxruntime"),
}
for modulo, (descripcion, instalar) in paquetes.items():
    try:
        importlib.import_module(modulo)
        filas.append((descripcion, "ok", True, ""))
    except Exception:
        filas.append((descripcion, "no está", False, f"{sys.executable} -m {instalar}"))
        falta_algo = True

ancho = max(len(f[0]) for f in filas) + 2
print()
for nombre, detalle, bien, receta in filas:
    print(f" {'✅' if bien else '❌'} {nombre.ljust(ancho)} {detalle}")
    if not bien and receta:
        print(f"      instala con:  {receta}")

print()
if falta_algo:
    print("Falta algo de la lista. Instálalo y vuelve a correr esta revisión.")
    sys.exit(1)
print("Todo listo para armar anuncios.")
