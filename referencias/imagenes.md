# Imágenes: ilustraciones, personaje, escenografía y fotos reales

## Cómo se pide una imagen

El plan (`guiones/<anuncio>.imagenes.json`) solo dice **qué** hay en la imagen, en inglés y en
pocas palabras. El **cómo** (técnica, paleta, acabado) lo pone el estilo, y el fondo plano y el
"sin texto" los pone el script. Nunca metas el estilo en el prompt: lo repetirías mal.

```json
{"slug": "julio-carrito", "tipo": "pose", "ref": ["julio-base"],
 "prompt": "serving coffee from his small street cart to a customer, morning street behind"}
```

Tipos:

| tipo | para qué | modelo por defecto |
|---|---|---|
| `personaje` | la base del protagonista (cara, edad, ropa) | `nano-banana-pro` |
| `pose` | el mismo personaje haciendo otra cosa (necesita `ref`) | `nano-banana-pro` |
| `objeto` | una cosa suelta | `nano-banana-2` |
| `escenografia` | el marco decorado de los bordes | `nano-banana-2` |

## El mismo personaje en todo el anuncio

1. Genera primero la base con una descripción específica: edad, pelo, ropa, colores, actitud.
   Mientras más concreta, más fácil de repetir.
2. Cada pose se pide con `"ref": ["<slug de la base>"]`. El script manda la imagen base como
   referencia y el modelo respeta cara, pelo y ropa.
3. Revisa la hoja de contacto: si una pose cambió de cara, vuelve a generarla
   (`--solo <slug> --rehacer`) y describe mejor la acción, no a la persona.

## La lección que cuesta caro: objetos sin contexto

Un objeto dibujado solo, sin persona ni entorno, se lee mal. Una silla médica dibujada sola
parece un inodoro; una máquina sola parece un electrodoméstico; un aparato solo parece un juguete.

**Regla:** si el objeto es el protagonista de la escena, pídelo **con la persona usándolo y con
el entorno alrededor** ("a woman sitting fully dressed on a medical chair in a clinic room, a
nurse and a monitor beside her"). Los objetos sueltos déjalos para cosas obvias: un reloj,
un celular, unas llaves, unas gotas.

Otra trampa: estos modelos quieren escribir texto en la imagen y casi siempre lo escriben mal o
en inglés. Por eso el prompt lleva *no text, no letters*. Si aun así aparece texto, regenera.

## Fondos y recortes

- Estilos claros → la imagen se genera sobre **verde o magenta plano** y se recorta por chroma.
- `pizarron`, `neon` y `plano` → se generan sobre **negro** y se recortan por luz: el brillo se
  convierte en opacidad, el trazo luminoso queda intacto.

Si queda un halo de color alrededor:

```bash
python -X utf8 pipeline/recortar.py material/imagenes-originales/algo.png public/recortes/algo.png \
  --estilo vintage-50s --tolerancia 1.5
```

Si el fondo salió con sombras o degradado, el chroma no alcanza: usa `--modo rembg`.

## Escenografía (el marco de los bordes)

Una sola por estilo, se reutiliza en todos los anuncios del proyecto. Se genera en 9:16 con el
centro vacío y el script le borra el centro y lo deja en 1080×1920 exactos.

Queda en `public/escenografia/<estilo>.png`. Si no existe, el video dibuja un marco propio de
colores del estilo (se ve bien, pero el generado luce mejor).

## Fotos de personas reales

A una persona real **nunca** se le redibuja la cara con IA: pierde el parecido y se nota.
Lo que hacemos es quitarle el fondo a la foto verdadera y llevarla al universo del estilo.

```bash
python -X utf8 pipeline/foto_real.py material/fotos/dueno.jpg dueno --estilo vintage-50s --fundido 0.15
```

- `--fundido 0.15` desvanece el borde de abajo (cuando la foto queda cortada a media pierna).
- `--ya-recortada` si la foto ya viene con fondo transparente.
- Cada estilo tiene su receta: duotono crema y rojo en `vintage-50s`, blanco y negro duro con
  sombras de persiana en `cine-negro`, trazo de tiza en `pizarron`, brillo neón en `neon`,
  grabado de líneas en `billete`, tramado de puntos en `pop-art`, etc.

Pide fotos de frente, con buena luz y sin otras personas al lado. Si la foto es de baja calidad,
mejor úsala pequeña (`alto={420}`) y en una esquina.

## Cuánto cuesta

`nano-banana-2` ≈ 0.04 USD por imagen; `nano-banana-pro` ≈ 0.12 USD. Un anuncio típico usa entre
6 y 12 imágenes (1 personaje base + 5–8 poses + 2–3 objetos + 1 escenografía): entre 1 y 2 USD.
Corre siempre primero sin `--si` para leer los prompts antes de gastar.
