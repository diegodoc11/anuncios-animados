"""Crea el archivo del anuncio ya armado: una escena por beat, con las palabras y sus
frames anotados arriba de cada una, y lo registra en src/anuncios/index.ts.

A partir de ahí solo hay que reemplazar los componentes de cada escena.

Uso:  python -X utf8 pipeline/esqueleto_anuncio.py a1 [--forzar]
"""
from __future__ import annotations

import argparse
import json

from comun import DATOS, RAIZ, cargar_guion, ok, salir

ap = argparse.ArgumentParser()
ap.add_argument("anuncio")
ap.add_argument("--forzar", action="store_true", help="sobrescribe el archivo si ya existe")
args = ap.parse_args()

guion = cargar_guion(f"guiones/{args.anuncio}.json")
ruta_palabras = DATOS / f"{args.anuncio}.palabras.json"
if not ruta_palabras.exists():
    salir("Faltan los tiempos. Corre estimar_tiempos.py o transcribir_voz.py primero.")
palabras = json.loads(ruta_palabras.read_text(encoding="utf-8"))

destino = RAIZ / "src" / "anuncios" / f"{args.anuncio}.tsx"
if destino.exists() and not args.forzar:
    salir(f"{destino} ya existe. Usa --forzar si quieres empezar de cero (se pierde lo escrito).")

def _corto(texto: str, maximo: int = 26) -> str:
    """Un pedacito del beat como texto de arranque (sin cortar palabras a la mitad)."""
    palabras_texto = texto.strip().lower().split()
    salida = ""
    for p in palabras_texto:
        if len(salida) + len(p) + 1 > maximo:
            break
        salida = f"{salida} {p}".strip()
    return (salida or palabras_texto[0])[:maximo].strip(" ,.;:")


escenas = []
mapa = []
for i, b in enumerate(guion["beats"], 1):
    nombre = f"Beat{i:02d}"
    lista = " ".join(f"{p}@{f}" for p, f in palabras.get(b["id"], []))
    escenas.append(f"""// ── {b['id']} · "{b['texto']}"
//    palabras: {lista}
const {nombre}: React.FC = () => (
  <>
    <Titular en="{(palabras.get(b['id']) or [['', 0]])[0][0]}" y={{45}} size={{140}} desde="abajo">
      {_corto(b['texto'])}
    </Titular>
  </>
);
""")
    mapa.append(f'  "{b["id"]}": {nombre},')

cabecera = f"""/* ANUNCIO {args.anuncio} · estilo: {guion.get('estilo', 'vintage-50s')}
 *  Banner: {guion.get('banner', '')}
 *
 *  Cada escena entra con la voz: en="palabra" usa los tiempos de
 *  src/data/{args.anuncio}.palabras.json (arriba de cada escena están las palabras y su frame).
 *  Si regeneras la voz, no toques nada: los tiempos se actualizan solos.
 */
import React from "react";
import {{
  Acto,
  CirculoBoceto,
  Contador,
  Etiqueta,
  FlechaMano,
  Imagen,
  Sello,
  Tachon,
  Titular,
}} from "../componentes/publico";
import manifest from "../data/{args.anuncio}.manifest.json";
import palabras from "../data/{args.anuncio}.palabras.json";
import type {{ DefinicionAnuncio, Escenas, Manifest, Palabra }} from "../tipos";

"""

pie = f"""const escenas: Escenas = {{
{chr(10).join(mapa)}
}};

export const anuncio: DefinicionAnuncio = {{
  id: "{args.anuncio}",
  estilo: "{guion.get('estilo', 'vintage-50s')}",
  banner: "{guion.get('banner', '')}",
  manifest: manifest as Manifest,
  palabras: palabras as unknown as Record<string, Palabra[]>,
  escenas,
  musica: {{ src: "musica/{args.anuncio}.mp3" }},
}};
"""

destino.write_text(cabecera + "\n".join(escenas) + "\n" + pie, encoding="utf-8")

# Registrar en el índice
import re

variable = re.sub(r"[^A-Za-z0-9_]", "_", args.anuncio)
indice = RAIZ / "src" / "anuncios" / "index.ts"
texto = indice.read_text(encoding="utf-8")
if f'from "./{args.anuncio}"' not in texto:
    linea_import = f'import {{ anuncio as {variable} }} from "./{args.anuncio}";'
    texto = texto.replace('import type { DefinicionAnuncio } from "../tipos";',
                          f'import type {{ DefinicionAnuncio }} from "../tipos";\n{linea_import}', 1)

    def _lista(m):
        actuales = [x.strip() for x in m.group(1).split(",") if x.strip()]
        if variable not in actuales:
            actuales.append(variable)
        return f"export const ANUNCIOS: DefinicionAnuncio[] = [{', '.join(actuales)}];"

    texto = re.sub(r"export const ANUNCIOS: DefinicionAnuncio\[\] = \[([^\]]*)\];", _lista, texto)
    indice.write_text(texto, encoding="utf-8")

ok(f"{destino.relative_to(RAIZ)} creado y registrado.")
print("Ahora escribe las escenas y revisa con:  python -X utf8 pipeline/revisar_anuncio.py " + args.anuncio)
