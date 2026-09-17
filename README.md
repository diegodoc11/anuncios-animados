# Anuncios Animados — skill de Claude Code

Pegas el guion de tu anuncio y te devuelve el video: **vertical 1080×1920, animado, con voz de IA,
ilustraciones, música y los textos entrando exactamente cuando la voz dice cada palabra.**
Listo para pautar en Meta, Instagram Reels o TikTok.

Hecha por [Diego Osorio](https://instagram.com/soydiegoosorio).

![10 estilos](https://img.shields.io/badge/estilos-10-c0392b) ![Remotion](https://img.shields.io/badge/render-Remotion-0b84f3) ![Licencia](https://img.shields.io/badge/licencia-MIT-2d6a5c)

## Instalar (copia y pega esto en Claude Code)

```
Instala esta skill de Claude Code: clónala desde https://github.com/diegodoc11/anuncios-animados dentro de ~/.claude/skills/ y corre su configuración de primera vez conmigo.
```

Claude clona la skill, revisa que tengas todo lo necesario, te pide tus llaves, te hace escuchar
voces para que elijas la tuya y deja lista tu carpeta de trabajo.

## Después, para hacer un anuncio

Pega tu guion y di:

```
hazme este anuncio animado
```

Claude te pregunta el CTA y el estilo, arma la locución, genera las ilustraciones, sincroniza
todo con la voz, te muestra un borrador para aprobar y entrega el video final.

## Qué necesitas

| | Para qué | Costo aproximado |
|---|---|---|
| Claude Code con plan de pago | quien arma todo | desde 20 USD/mes |
| Cuenta en [kie.ai](https://kie.ai) | ilustraciones (Nano Banana) y música (Suno) | ~1–2 USD por anuncio |
| Cuenta en [elevenlabs.io](https://elevenlabs.io) | la voz | ~900 caracteres por anuncio |
| Node.js 18+, ffmpeg, Python 3.9+ | el motor del video | gratis |

La skill revisa todo eso sola y te dice qué instalar si falta algo.

## Los 10 estilos

`vintage-50s` · `cine-negro` · `pizarron` · `neon` · `billete` · `pop-art` · `andino` · `plano` ·
`sellos-oficina` · `mapa-expedicion`

Cada estilo trae su paleta, su tipografía, su textura, su marco decorado, su receta de
ilustración, su forma de estilizar fotos reales y su estilo de música.
Ver `referencias/estilos.md`.

## Lo que hace distinto a esta skill

- **Sincronización por palabra.** Se transcribe la locución con tiempos por palabra: en el código
  escribes `en="pañal"` y el gráfico entra en el frame exacto en que se oye "pañal".
  Si mañana cambias la voz, todo el anuncio se re-sincroniza solo.
- **Verificación de la locución.** Compara lo que se oyó contra el guion y avisa si la voz se
  comió una palabra. Nada de anuncios que dicen algo distinto a lo aprobado.
- **Ritmo apretado.** Recorta silencios y acelera 1.1x sin cambiar el tono: 21 segundos de voz
  quedan en 17, y eso se nota en la retención.
- **El mismo personaje en todo el video.** Se genera un personaje base y cada pose se pide con
  esa imagen como referencia.
- **Personas reales sin deformar.** A una persona real no se le redibuja la cara: se le quita el
  fondo a su foto y se estiliza para que pertenezca al anuncio.
- **Maqueta gratis.** Puedes armar y revisar el anuncio completo, con tiempos estimados y
  marcadores donde irán las imágenes, antes de gastar un crédito.
- **Audio de verdad:** música original con Suno, efectos sintetizados con ffmpeg (nada de audio
  de terceros) y mezcla final a -14 LUFS.

## Estructura

```
SKILL.md                 instrucciones para Claude
referencias/             estilos, componentes, guion y voz, imágenes, calidad
scripts/                 configuración, casting de voces, crear proyecto
assets/template/         proyecto Remotion que se copia a cada marca
  src/                   componentes y estilos del video
  pipeline/              voz, transcripción, imágenes, música, revisión y export
```

## Licencia

MIT — ver [LICENSE](LICENSE).
