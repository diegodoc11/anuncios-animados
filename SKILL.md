---
name: anuncios-animados
description: Convierte un guion de anuncio (gancho → cuerpo → CTA) en un video VERTICAL ANIMADO de 1080x1920 listo para pautar en Meta, Instagram Reels o TikTok. Genera la locución con IA, sincroniza cada texto e imagen con la palabra exacta que se escucha, ilustra con Nano Banana manteniendo el mismo personaje en todo el video, estiliza fotos reales de personas, pone música original y exporta el video con el audio nivelado. Trae 10 estilos visuales (vintage años 50, cine negro, pizarrón, neón, billete grabado, cómic pop-art, textil andino, plano de ingeniería, sellos de oficina, mapa de expedición). Úsala cuando el usuario pegue un guion y diga "hazme este anuncio animado", "anima este guion", "conviértelo en video", "anuncio animado para Meta/TikTok", o invoque /anuncios-animados.
---

# Anuncios animados

Tú (el modelo) armas el video. El usuario solo trae el guion y aprueba.
El resultado es un MP4 vertical animado: voz con IA, ilustraciones en un estilo, textos que
entran sincronizados con la voz, música y efectos de sonido.

**Regla que manda sobre todas:** nada entra "más o menos". Cada texto y cada imagen entra en el
frame exacto en el que la voz dice esa palabra. Eso lo resuelve el motor de tiempos: tú solo
escribes `en="palabra"`.

---

## 0. Antes de nada: ¿ya está configurada?

```bash
python -X utf8 "<SKILL>/scripts/configurar.py" estado
```

`<SKILL>` es la carpeta donde está este archivo (normalmente `~/.claude/skills/anuncios-animados`).

- Si dice **Configuración completa** → salta a la sección 2.
- Si falta algo → haz el asistente de primera vez (sección 1).

---

## 1. Primera vez (asistente)

Hazlo **de a un paso**, conversando. No pidas todo junto: el usuario es marketero, no programador.

**1.1 Revisar el computador**

```bash
python -X utf8 "<SKILL>/scripts/revisar_dependencias.py"
```

Si algo sale en rojo, dile al usuario el comando exacto que imprime el script y espera a que lo instale.

**1.2 Llave de Kie.ai** (imágenes y música). Dile: *"Entra a kie.ai, crea la cuenta, ve a API Key
y pégamela aquí"*. Cuando la pegue:

```bash
python -X utf8 "<SKILL>/scripts/configurar.py" llave KIE_API_KEY <valor>
```

**1.3 Llave de ElevenLabs** (voz). *"Entra a elevenlabs.io → tu foto → API Keys → crea una y pégamela"*.

```bash
python -X utf8 "<SKILL>/scripts/configurar.py" llave ELEVENLABS_API_KEY <valor>
```

Las dos quedan guardadas en la carpeta personal del usuario, **nunca** dentro de un proyecto.

**1.4 Elegir la voz.** Pregunta: idioma/acento (colombiano, mexicano, argentino, neutro…), hombre
o mujer, y qué tono quiere (cercano, serio, joven). Luego:

```bash
python -X utf8 "<SKILL>/scripts/buscar_voces.py" --idioma es --acento colombian --genero female --n 6
```

Pásale las muestras gratis (`preview_url`) para que escuche. Si quiere oírlas diciendo lo mismo
—es la forma honesta de comparar— avísale cuántos caracteres cuesta y genera solo con permiso:

```bash
python -X utf8 "<SKILL>/scripts/buscar_voces.py" --idioma es --acento colombian --genero female --n 5 \
  --frase "<una frase del guion del usuario>" --generar --si
```

Cuando elija:

```bash
python -X utf8 "<SKILL>/scripts/configurar.py" voz <voice_id> "<nombre>"
```

**1.5 Perfil de marca.** Pregunta el nombre del negocio, el CTA que usa siempre y si tiene un
estilo favorito de los 10 (muéstrale la lista de `referencias/estilos.md`).

```bash
python -X utf8 "<SKILL>/scripts/configurar.py" marca --negocio "Café La Esquina" --cta "Toca el botón" --estilo vintage-50s
```

Si hay nombres que la voz lee mal (marcas, apellidos), guárdalos:

```bash
python -X utf8 "<SKILL>/scripts/configurar.py" pronunciacion "Kie.ai" "Kaiei"
```

**1.6 Crear la carpeta de trabajo** (una por marca o cliente):

```bash
python -X utf8 "<SKILL>/scripts/nuevo_proyecto.py" "<carpeta del proyecto>"
```

Instala Remotion y crea los efectos de sonido. **Todos los comandos de la sección 2 se corren
dentro de esa carpeta.**

---

## 2. Hacer un anuncio (el flujo completo)

### Paso 1 — Entender el encargo

Pregunta solo lo que no puedas deducir del guion:

1. **El CTA**: ¿a dónde lleva el botón y qué quieres que haga la persona? (siempre, antes de escribir nada)
2. **El estilo** (los 10 están en `referencias/estilos.md`). Recomienda uno según el tema y deja que decida.
3. **El banner-gancho**: la promesa que se queda arriba todo el video. Máximo ~34 caracteres.
4. Si hay una persona real (el dueño, el doctor, él mismo): pídele la foto.

### Paso 2 — Partir el guion en beats

Un beat = una idea = una frase que se puede decir de corrido (2–6 segundos). Escribe
`guiones/<anuncio>.json` (el id del anuncio es corto: `a1`, `a2`…):

```json
{
  "id": "a1",
  "estilo": "vintage-50s",
  "banner": "de 12 cafés al día a 11.200 al mes",
  "beats": [
    {"id": "a1-01", "texto": "Don Julio vendía 12 cafés al día en la esquina de su barrio."},
    {"id": "a1-02", "texto": "Probó volantes, probó descuentos. Nada movió la aguja."}
  ]
}
```

Reglas del texto: como se habla, no como se escribe. Las cifras se pueden dejar con números
(el pipeline las convierte a palabras para la voz: `11.200` → *once mil doscientos*).
Detalles en `referencias/guion-y-voz.md`.

### Paso 3 — Maqueta sin gastar (opcional pero recomendado)

```bash
python -X utf8 pipeline/estimar_tiempos.py guiones/a1.json
python -X utf8 pipeline/esqueleto_anuncio.py a1
```

Ya puedes escribir las escenas y ver el anuncio completo (con marcadores donde irán las imágenes)
antes de gastar un solo crédito. Cuando llegue la voz real, los tiempos se reemplazan solos.

### Paso 4 — Locución

```bash
python -X utf8 pipeline/gen_voz.py guiones/a1.json          # muestra el texto y cuánto cuesta
python -X utf8 pipeline/gen_voz.py guiones/a1.json --si     # genera (gasta créditos)
```

Muéstrale al usuario cuántos caracteres va a gastar **antes** de usar `--si`.

```bash
python -X utf8 pipeline/apretar_voz.py guiones/a1.json        # recorta silencios y acelera 1.1x
python -X utf8 pipeline/transcribir_voz.py guiones/a1.json    # tiempos por palabra + verificación
```

`transcribir_voz.py` te dice si la voz se comió alguna palabra. Si avisa de un beat, bájale el
tempo a ese beat (`"tempo": 1.0` en el guion) y repite `apretar_voz.py` + `transcribir_voz.py`.
**No sigas con un beat en rojo**: el anuncio quedaría diciendo algo distinto al guion.

### Paso 5 — Imágenes

Escribe el plan `guiones/a1.imagenes.json` (ver `referencias/imagenes.md` para prompts que funcionan):

```json
{
  "estilo": "vintage-50s",
  "imagenes": [
    {"slug": "julio-base", "tipo": "personaje", "prompt": "a 62-year-old coffee seller, grey moustache, brown apron"},
    {"slug": "julio-carrito", "tipo": "pose", "ref": ["julio-base"], "prompt": "serving coffee from his small street cart"},
    {"slug": "marco", "tipo": "escenografia"}
  ]
}
```

```bash
python -X utf8 pipeline/gen_imagenes.py guiones/a1.imagenes.json         # muestra los prompts, no gasta
python -X utf8 pipeline/gen_imagenes.py guiones/a1.imagenes.json --si    # genera y recorta
python -X utf8 pipeline/hoja_contacto.py revision/recortes.png --estilo vintage-50s
```

**Mira la hoja de contacto** (ábrela, léela con tus ojos). Dos cosas que siempre hay que revisar:
el personaje debe ser el mismo en todas las poses, y ningún objeto puede leerse como otra cosa.
Un objeto dibujado solo, sin persona ni contexto, engaña: siempre ponlo en la escena completa
(persona + objeto + entorno).

Si hay foto de una persona real:

```bash
python -X utf8 pipeline/foto_real.py material/fotos/dueno.jpg dueno --estilo vintage-50s --fundido 0.15
```

A las personas reales **nunca** se les redibuja la cara con IA.

### Paso 6 — Música y sonido

```bash
python -X utf8 pipeline/gen_musica.py a1 --estilo vintage-50s --si
python -X utf8 pipeline/preparar_musica.py guiones/a1.json material/musica-original/a1-1.mp3
```

Los efectos (`whoosh`, `pop`, `click`, `golpe`, `papel`, `ding`) ya existen; si falta alguno:
`python -X utf8 pipeline/crear_sfx.py`.

### Paso 7 — Escribir las escenas

Abre `src/anuncios/a1.tsx` (lo creó `esqueleto_anuncio.py`, con las palabras y sus frames
anotadas arriba de cada escena) y arma cada beat con los componentes.
El catálogo completo, con ejemplos, está en `referencias/componentes.md`.

Lo esencial:

```tsx
// ── a1-01 · "Don Julio vendía 12 cafés al día…"
//    palabras: Don@0 Julio@8 vendía@21 doce@35 cafés@46 al@58 día@64 …
const Beat01: React.FC = () => (
  <>
    <Imagen src="recortes/julio-carrito.png" y={44} alto={700} desde="abajo" sfx="whoosh" />
    <Contador en="doce" hasta={12} sufijo=" cafés" y={74} size={150} sfx="pop" />
    <Etiqueta en="esquina" y={84}>al día, en la esquina del barrio</Etiqueta>
  </>
);
```

Reglas de oro al escribir escenas:

- `en="palabra"` en todo lo que entra. Números sueltos (`delay={12}`) solo para remates.
- Varias cosas dentro del mismo beat → `<Acto desde="…" hasta="…">` (los hijos cuentan su
  tiempo desde que arranca el acto).
- Nada de fundidos: todo entra deslizándose (`desde="izquierda" | "derecha" | "arriba" | "abajo" | "centro" | "sello"`).
- Ancho útil entre los bordes: **860 px**. Un titular en Anton mide ≈ 0.42 × tamaño × nº de caracteres
  → tamaño máximo ≈ 2050 / caracteres. Si no cabe, pártelo con `\n` o acorta el texto.
- El banner de arriba se ve todo el video: no pongas nada por encima de y=12.

### Paso 8 — Revisar antes de renderizar

```bash
python -X utf8 pipeline/revisar_anuncio.py a1
```

Arregla lo que salga en rojo (una palabra mal escrita en un `en=` rompe el render).

### Paso 9 — Borrador, hoja de contacto y aprobación

```bash
npx remotion render src/index.ts a1 out/a1-borrador.mp4 --scale=0.5
python -X utf8 pipeline/hoja_frames.py out/a1-borrador.mp4 revision --anuncio a1
```

**Abre las hojas y míralas** (con la herramienta de leer imágenes). Revisa:

1. ningún texto toca ni pasa las líneas rosadas (el ancho útil);
2. cada imagen aparece cuando se nombra, no antes ni después;
3. el banner se ve completo arriba;
4. ningún beat quedó vacío ni con el marcador punteado de "falta imagen".

Corrige y repite. Cuando esté bien, **muéstrale el borrador al usuario y espera su OK**.

### Paso 10 — Render final

```bash
npx remotion render src/index.ts a1 out/a1.mp4
python -X utf8 pipeline/finalizar.py out/a1.mp4
```

Entrega `out/a1-final.mp4` (audio a -14 LUFS, listo para pautar) y `out/a1-celular.mp4`
(menos de 30 MB, para WhatsApp o para que lo vea en el teléfono).

---

## 3. Cómo hablarle al usuario

- Nada de jerga. No digas "componente", "render", "chroma": di "la escena", "armar el video",
  "quitarle el fondo".
- Antes de cada gasto (voz, imágenes, música), dile qué va a costar y espera el sí.
- Cuando algo se puede decidir solo (colores, tiempos, qué componente usar), decídelo tú.
  Él decide: guion, estilo, CTA, si aprueba el borrador.

## 4. Si algo falla

| Qué ves | Qué pasa | Cómo se arregla |
|---|---|---|
| `No encuentro la palabra "x" en la locución` | el `en=` no coincide con lo que se oyó | mira las palabras anotadas arriba de la escena y usa una de esas |
| El render se cae en un beat | casi siempre es un ancla mala | `python -X utf8 pipeline/revisar_anuncio.py <id>` |
| Sale un marcador punteado | falta esa imagen en `public/recortes/` | genera la imagen o corrige el nombre |
| La voz se comió una palabra | el 1.1x fue mucho para ese beat | `"tempo": 1.0` en ese beat y repite apretar + transcribir |
| `invalid_api_key` en ElevenLabs | se está usando el **ID** de la llave, no la llave | la llave buena empieza por `sk_`; vuelve a copiarla y guárdala con `configurar.py llave ELEVENLABS_API_KEY` |
| El recorte quedó con halo verde | el fondo del dibujo no era plano | `pipeline/recortar.py <original> <destino> --estilo <estilo> --tolerancia 1.5` |
| La música tapa la voz | quedó alta | `preparar_musica.py … --debajo 18` |
| Todo entra tarde o temprano | cambiaste la voz y no re-transcribiste | vuelve a correr `transcribir_voz.py` (los tiempos se re-sincronizan solos) |

## 5. Referencias

- `referencias/estilos.md` — los 10 estilos, para qué sirve cada uno y qué música le va.
- `referencias/componentes.md` — catálogo de componentes con ejemplos copiables.
- `referencias/guion-y-voz.md` — cómo partir el guion, cifras, pronunciación y ritmo.
- `referencias/imagenes.md` — prompts, personaje consistente, escenografía y fotos reales.
- `referencias/calidad.md` — lista de control antes de entregar.
