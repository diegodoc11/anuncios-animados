"""Cosas que usan todos los scripts del pipeline: rutas, llaves, guiones,
números escritos en palabras y utilidades de audio/HTTP.

Funciona igual en Windows, macOS y Linux. Siempre correr con:  python -X utf8 ...
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.request

# ── Rutas ───────────────────────────────────────────────────────────────────────
RAIZ = pathlib.Path(__file__).resolve().parent.parent
GUIONES = RAIZ / "guiones"
MATERIAL = RAIZ / "material"          # originales pesados: NO entran al render
PUBLICO = RAIZ / "public"             # lo que sí usa Remotion
DATOS = RAIZ / "src" / "data"
VOZ_ORIGINAL = MATERIAL / "voz-original"
VOZ = PUBLICO / "voz"
RECORTES = PUBLICO / "recortes"
ESCENOGRAFIA = PUBLICO / "escenografia"
MUSICA = PUBLICO / "musica"
SFX = PUBLICO / "sfx"
IMAGENES_ORIGINALES = MATERIAL / "imagenes-originales"
MUSICA_ORIGINAL = MATERIAL / "musica-original"
FPS = 30

DIR_CONFIG = pathlib.Path(os.environ.get("ANUNCIOS_ANIMADOS_CONFIG", pathlib.Path.home() / ".config" / "anuncios-animados"))
ARCHIVO_LLAVES = DIR_CONFIG / "llaves.env"
ARCHIVO_PERFIL = DIR_CONFIG / "perfil.json"


def crear_carpetas() -> None:
    for c in (GUIONES, MATERIAL, PUBLICO, DATOS, VOZ_ORIGINAL, VOZ, RECORTES, ESCENOGRAFIA, MUSICA, SFX,
              IMAGENES_ORIGINALES, MUSICA_ORIGINAL):
        c.mkdir(parents=True, exist_ok=True)


# ── Llaves y perfil ─────────────────────────────────────────────────────────────
def llaves() -> dict:
    datos = {}
    if ARCHIVO_LLAVES.exists():
        for linea in ARCHIVO_LLAVES.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                k, v = linea.split("=", 1)
                datos[k.strip()] = v.strip()
    return datos


def llave(nombre: str, obligatoria: bool = True) -> str:
    # Manda lo que guardó la configuración de la skill; la variable de entorno es el respaldo.
    # (En muchos computadores hay variables viejas de otras herramientas que ya no sirven.)
    valor = llaves().get(nombre, "") or os.environ.get(nombre, "")
    if valor and nombre == "ELEVENLABS_API_KEY" and not valor.startswith("sk_"):
        aviso("Esa llave de ElevenLabs no parece una llave: las buenas empiezan por 'sk_' "
              "(lo que hay se parece más al ID de la llave). Vuelve a copiarla desde elevenlabs.io.")
    if not valor and obligatoria:
        salir(f"Falta {nombre}. Corre la configuración de la skill (scripts/configurar.py) "
              f"o define la variable de entorno {nombre}.")
    return valor


def perfil() -> dict:
    if ARCHIVO_PERFIL.exists():
        return json.loads(ARCHIVO_PERFIL.read_text(encoding="utf-8"))
    return {}


# ── Guiones ─────────────────────────────────────────────────────────────────────
def cargar_guion(ruta: str | pathlib.Path) -> dict:
    p = pathlib.Path(ruta)
    if not p.exists():
        p2 = GUIONES / p.name
        if p2.exists():
            p = p2
        else:
            salir(f"No encuentro el guion {ruta}")
    guion = json.loads(p.read_text(encoding="utf-8"))
    guion["_ruta"] = str(p)
    guion.setdefault("id", p.stem)
    if not guion.get("beats"):
        salir(f"El guion {p} no tiene beats.")
    for i, b in enumerate(guion["beats"], 1):
        b.setdefault("id", f"{guion['id']}-{i:02d}")
        if not b.get("texto"):
            salir(f"El beat {b['id']} no tiene texto.")
    return guion


# ── Números a palabras (para que la voz no lea cifras raras) ─────────────────────
_UNIDADES = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
             "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho",
             "diecinueve", "veinte", "veintiuno", "veintidós", "veintitrés", "veinticuatro",
             "veinticinco", "veintiséis", "veintisiete", "veintiocho", "veintinueve"]
_DECENAS = {3: "treinta", 4: "cuarenta", 5: "cincuenta", 6: "sesenta", 7: "setenta", 8: "ochenta", 9: "noventa"}
_CENTENAS = {1: "ciento", 2: "doscientos", 3: "trescientos", 4: "cuatrocientos", 5: "quinientos",
             6: "seiscientos", 7: "setecientos", 8: "ochocientos", 9: "novecientos"}


def _menor_cien(n: int) -> str:
    if n < 30:
        return _UNIDADES[n]
    d, u = divmod(n, 10)
    return _DECENAS[d] if u == 0 else f"{_DECENAS[d]} y {_UNIDADES[u]}"


def _menor_mil(n: int) -> str:
    if n < 100:
        return _menor_cien(n)
    c, r = divmod(n, 100)
    if n == 100:
        return "cien"
    return _CENTENAS[c] if r == 0 else f"{_CENTENAS[c]} {_menor_cien(r)}"


def _apocope(texto: str) -> str:
    """veintiuno → veintiún, uno → un (antes de un sustantivo o de 'mil')."""
    if texto.endswith("veintiuno"):
        return texto[:-9] + "veintiún"
    if texto.endswith("uno"):
        return texto[:-3] + "un"
    return texto


def numero_a_letras(n: int, apocope: bool = False) -> str:
    n = int(n)
    if n < 0:
        return "menos " + numero_a_letras(-n, apocope)
    if n < 1000:
        t = _menor_mil(n)
    elif n < 1_000_000:
        miles, r = divmod(n, 1000)
        pre = "mil" if miles == 1 else f"{_apocope(_menor_mil(miles))} mil"
        t = pre if r == 0 else f"{pre} {_menor_mil(r)}"
    else:
        millones, r = divmod(n, 1_000_000)
        pre = "un millón" if millones == 1 else f"{_apocope(numero_a_letras(millones))} millones"
        t = pre if r == 0 else f"{pre} {numero_a_letras(r)}"
    return _apocope(t) if apocope else t


_NUM_MILES = re.compile(r"\b\d{1,3}(?:\.\d{3})+\b")
_NUM_DECIMAL = re.compile(r"\b(\d+),(\d+)\b")
_NUM_PORCENTAJE = re.compile(r"\b(\d+)\s*%")
_NUM_SIMPLE = re.compile(r"\b\d+\b")


def cifras_a_palabras(texto: str) -> str:
    """11.200 → once mil doscientos · 24 años → veinticuatro años · 50% → cincuenta por ciento."""
    def _miles(m):
        return numero_a_letras(int(m.group(0).replace(".", "")))

    def _decimal(m):
        return f"{numero_a_letras(int(m.group(1)))} coma {numero_a_letras(int(m.group(2)))}"

    def _porcentaje(m):
        return f"{numero_a_letras(int(m.group(1)))} por ciento"

    def _simple_sobre(cadena):
        def _f(m):
            n = int(m.group(0))
            resto = cadena[m.end():m.end() + 3]
            # "21 años" → veintiún años · "21" solo → veintiuno
            return numero_a_letras(n, apocope=bool(re.match(r"\s+[a-zA-ZáéíóúñÁÉÍÓÚÑ]", resto)))
        return _f

    t = _NUM_MILES.sub(_miles, texto)
    t = _NUM_DECIMAL.sub(_decimal, t)
    t = _NUM_PORCENTAJE.sub(_porcentaje, t)
    t = _NUM_SIMPLE.sub(_simple_sobre(t), t)
    return t


def texto_para_voz(texto: str, pronunciacion: dict | None = None) -> str:
    """Texto listo para el generador de voz: cifras en palabras y marcas de pronunciación."""
    t = cifras_a_palabras(texto)
    for original, como_suena in (pronunciacion or {}).items():
        t = re.sub(rf"\b{re.escape(original)}\b", como_suena, t, flags=re.IGNORECASE)
    return t


def normalizar(palabra: str) -> str:
    p = unicodedata.normalize("NFD", palabra.lower())
    p = "".join(c for c in p if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", p)


# ── Audio / procesos ────────────────────────────────────────────────────────────
def hay(programa: str) -> bool:
    return shutil.which(programa) is not None


def correr(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode != 0:
        salir(f"Falló:\n  {' '.join(cmd[:6])} …\n{(r.stderr or r.stdout or '')[-1500:]}")
    return r


def duracion(archivo: pathlib.Path) -> float:
    r = correr(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(archivo)])
    return float(r.stdout.strip())


def loudness(archivo: pathlib.Path) -> float:
    """LUFS integrados del archivo (para nivelar la música bajo la voz)."""
    r = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(archivo), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    bloque = re.findall(r"\{[^{}]*input_i[^{}]*\}", r.stderr, re.S)
    if not bloque:
        salir(f"No pude medir el volumen de {archivo.name}")
    return float(json.loads(bloque[-1])["input_i"])


# ── HTTP ────────────────────────────────────────────────────────────────────────
def pedir(url: str, headers: dict, cuerpo: dict | None = None, metodo: str | None = None,
          binario: bool = False, timeout: int = 180):
    datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, headers=headers, method=metodo or ("POST" if datos else "GET"))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            crudo = r.read()
    except urllib.error.HTTPError as e:
        salir(f"HTTP {e.code} en {url.split('?')[0]}\n{e.read()[:600].decode('utf-8', 'replace')}")
    except urllib.error.URLError as e:
        salir(f"No pude conectarme a {url.split('?')[0]}: {e.reason}")
    return crudo if binario else json.loads(crudo.decode("utf-8"))


def descargar(url: str, destino: pathlib.Path, timeout: int = 300) -> pathlib.Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        destino.write_bytes(r.read())
    return destino


def guardar_palabras(ruta, palabras_por_beat: dict) -> None:
    """Una línea por beat: se lee fácil y el diff no se vuelve un monstruo."""
    cuerpo = ",\n".join(f' "{k}": ' + json.dumps(v, ensure_ascii=False) for k, v in palabras_por_beat.items())
    pathlib.Path(ruta).write_text("{\n" + cuerpo + "\n}\n", encoding="utf-8")


def salir(mensaje: str) -> None:
    print(f"\n❌ {mensaje}\n", flush=True)
    sys.exit(1)


def aviso(mensaje: str) -> None:
    print(f"⚠️  {mensaje}", flush=True)


def ok(mensaje: str) -> None:
    print(f"✅ {mensaje}", flush=True)
