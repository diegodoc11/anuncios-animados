# Los 10 estilos

Cada estilo define todo de golpe: color de fondo, textura, tipografía de las etiquetas,
colores de tinta y acento, el marco decorado de los bordes, cómo se generan las ilustraciones,
cómo se estilizan las fotos reales y qué música le va.

Los datos exactos (colores, prompts) viven en `assets/template/src/estilos.json`.
Ese archivo lo leen tanto el video (TypeScript) como el pipeline (Python): una sola fuente.

| id | Nombre | Cuándo usarlo | Se siente |
|---|---|---|---|
| `vintage-50s` | Anuncio vintage años 50 | testimonios, transformaciones, salud, hogar, comida | cálido, confiable, nostálgico |
| `cine-negro` | Cine negro | "lo que nadie te cuenta", problemas ocultos, denuncias | tenso, serio, cinematográfico |
| `pizarron` | Pizarrón de tiza | explicar un método o unos pasos, educación, consultoría | didáctico, cercano, claro |
| `neon` | Letrero de neón | ofertas, lanzamientos, eventos, tecnología, noche | urgente, moderno, eléctrico |
| `billete` | Billete grabado | dinero, ahorro, inversión, precios, ganancias | serio, valioso, financiero |
| `pop-art` | Cómic pop-art | ganchos explosivos, humor, público joven | ruidoso, divertido, directo |
| `andino` | Textil andino / precolombino | marcas latinoamericanas, turismo, gastronomía, artesanía | orgulloso, local, cálido |
| `plano` | Plano de ingeniería | "cómo funciona", procesos, sistemas, construcción | técnico, preciso, confiable |
| `sellos-oficina` | Trámite: sellos y carpetas | burocracia, papeleo, seguros, legal, humor de oficina | irónico, gris, reconocible |
| `mapa-expedicion` | Mapa de expedición | viajes, rutas, "el camino para lograr X", planes por etapas | aventurero, narrativo |

## Cómo elegir

1. **Por el tema**: ¿el guion habla de plata? `billete`. ¿De un método? `pizarron` o `plano`.
   ¿De una transformación personal? `vintage-50s` o `cine-negro`.
2. **Por el público**: mayores de 45 → `vintage-50s`, `mapa-expedicion`. Menores de 30 → `neon`, `pop-art`.
3. **Por el tono del gancho**: si el gancho es un problema doloroso, un estilo oscuro
   (`cine-negro`) da peso; si es una promesa alegre, uno claro (`vintage-50s`, `andino`).

Muéstrale al usuario el estilo antes de producir: en cualquier proyecto están registradas las
composiciones `muestra-<estilo>` con el anuncio de ejemplo. Renderiza un frame:

```bash
npx remotion still src/index.ts muestra-neon out/muestra-neon.png --frame=300 --scale=0.5
```

## Detalles que cambian con el estilo

- **Fondo de las ilustraciones.** Los estilos claros se generan sobre un color plano (verde o
  magenta) y se recorta por chroma. `pizarron`, `neon` y `plano` se generan **sobre negro** y se
  recortan por luz: el brillo se convierte en opacidad, así el trazo luminoso o de tiza se
  conserva igual que en el estilo.
- **Borde de sticker.** Los estilos claros llevan un contorno crema alrededor del recorte; los
  oscuros no llevan.
- **Fuente de las etiquetas.** Máquina de escribir en `cine-negro` y `sellos-oficina`, tiza en
  `pizarron`, cómic en `pop-art`, monoespaciada en `plano`, etc. El titular siempre es Anton.
- **Música sugerida.** Cada estilo trae su descripción musical para Suno; `gen_musica.py --estilo <id>`
  la usa sola.

## Cambiar un estilo o agregar uno nuevo

Edita `src/estilos.json` del proyecto (o del template, si quieres que quede para siempre).
Un estilo nuevo necesita las mismas claves que los otros. Lo más importante:

- `promptImagen`: la receta de arte en inglés (técnica, paleta, acabado).
- `promptEscenografia`: qué se dibuja en la banda de los bordes.
- `recorte.modo`: `chroma` (fondo plano de color) o `luz` (fondo negro).
- `efectoTitular`: `ninguno`, `sombra-dura`, `brillo`, `tiza`, `comic` o `grabado`.
- `foto`: cuál de las 10 recetas de `pipeline/foto_real.py` se le aplica a las fotos reales.
