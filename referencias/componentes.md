# Catálogo de componentes

Todos se importan de `../componentes/publico` dentro de `src/anuncios/<anuncio>.tsx`.

## Lo que comparten todos (props de posición y entrada)

| prop | qué hace | por defecto |
|---|---|---|
| `x`, `y` | centro del elemento, en % del cuadro (x=50 es el centro) | `x=50` |
| `en` | **palabra de la locución** en la que entra | — |
| `delay` | frames extra (o frames desde el inicio del acto, si no hay `en`) | `0` |
| `desde` | por dónde entra: `izquierda`, `derecha`, `arriba`, `abajo`, `centro`, `sello`, `no` | según el componente |
| `rotar` | grados de inclinación | según el componente |
| `escala` | tamaño relativo | `1` |
| `sfx` | efecto de sonido al entrar: `whoosh`, `pop`, `click`, `golpe`, `papel`, `ding` | — |
| `sfxVolumen` | 0 a 1 | `0.5` |

### Anclas de tiempo (`en=`)

```tsx
en="pañal"        // la primera vez que se dice "pañal"
en="noche#2"      // la segunda vez que se dice "noche"
en="dos años"     // grupo de palabras seguidas (entra con la primera)
en="gotitas+8"    // 8 frames después de esa palabra
en="resto-4"      // 4 frames antes
en={45}           // frame fijo, contado desde el inicio del acto
```

Las palabras disponibles de cada beat están anotadas en un comentario arriba de cada escena
(las escribe `esqueleto_anuncio.py`) y salen de `src/data/<anuncio>.palabras.json`.
Si escribes una palabra que no se dijo, el render se detiene y te dice cuáles hay: eso es a
propósito, es mejor que un texto entrando en el momento equivocado.

---

## Titular

Palabra o frase grande, en mayúsculas condensadas (Anton). Es el texto que la gente lee sin sonido.

```tsx
<Titular en="cincuenta" y={72} size={160}>58 años</Titular>
<Titular en="nada" y={45} size={200} acento>nada funcionó</Titular>
<Titular en="grada" y={70} size={120} desde="derecha">{"al bajar\nuna grada"}</Titular>
```

- `size`: tamaño pedido. Si no cabe en el ancho útil (860 px) se reduce solo.
- `acento`: lo pinta con el color de acento del estilo.
- `color`: color libre.
- `\n` parte líneas (dentro de `{" "}`, como en el tercer ejemplo).
- Regla de bolsillo: tamaño máximo ≈ **2050 / número de caracteres**.

## Etiqueta

Frase de apoyo sobre un papelito. Se parte sola en varias líneas.

```tsx
<Etiqueta en="esquina" y={84}>al día, en la esquina del barrio</Etiqueta>
<Etiqueta y={16} size={44} desde="arriba">la historia de don julio</Etiqueta>
```

Máximo 2 líneas: si se pasa, acórtala. `revisar_anuncio.py` avisa.

## Sello

Golpe seco de sello de caucho, con borde y tinta gastada. Para veredictos: *rechazado*,
*aprobado*, *no funcionó*, *hoy*.

```tsx
<Sello en="aguja" y={62} sfx="golpe">cero movimiento</Sello>
<Sello en="hoy" y={18} color="#1f7a72">hoy</Sello>
```

## Contador

Número que sube. Separador de miles en formato colombiano (11.200).

```tsx
<Contador en="once" hasta={11200} sufijo=" cafés" y={46} size={190} duracion={26} sfx="pop" />
<Contador en="ochenta" hasta={80} prefijo="" sufijo="%" y={50} />
```

## Imagen

Una ilustración recortada (PNG con transparencia) de `public/recortes/`.

```tsx
<Imagen src="recortes/julio-carrito.png" y={44} alto={700} desde="abajo" sfx="whoosh" />
<Imagen src="recortes/gotas.png" x={78} y={58} alto={320} en="gotitas" rebote />
<Imagen src="recortes/senora-estornudo.png" y={45} alto={700} temblor="x" amplitud={3} />
```

- `alto` en píxeles (el cuadro completo mide 1920 de alto).
- `temblor="x" | "y"`: vibración continua (nervios, peso, alarma).
- `rebote`: flotación suave (gotas, globos, celular).
- `voltear`: espeja la imagen.
- Si el archivo no existe, se dibuja un marcador punteado con el nombre: así puedes armar el
  anuncio antes de generar las imágenes.

## Acto — varias escenas dentro del mismo beat

Cuando en una sola frase pasan dos o tres cosas.

```tsx
<Acto hasta="Nada" sale="izquierda">
  <Titular en="volantes" y={32} size={120} desde="izquierda">volantes</Titular>
  <Titular en="descuentos" y={47} size={120} desde="derecha">descuentos</Titular>
</Acto>
<Acto desde="Nada" entra="derecha">
  <Titular y={44} size={210} acento>nada</Titular>
</Acto>
```

- `desde` / `hasta`: palabras (o frames) donde empieza y termina el acto.
- `entra` / `sale`: el grupo completo entra o se va deslizándose.
- Dentro del acto, los `delay={n}` cuentan desde que el acto arranca.

## Tachon — raya de marcador

Para tachar lo que ya no sirve (el método viejo, el precio anterior).

```tsx
<Tachon en="galletas+14" y={62} ancho={700} sfx="papel" />
<Tachon y={40} ancho={620} delay={10} color="#c0392b" grosor={20} />
```

Ponlo a la misma `y` del texto que quieres tachar.

## CirculoBoceto — círculo a mano

Para señalar lo importante.

```tsx
<CirculoBoceto en="segundos+6" y={85} ancho={760} alto={140} />
```

## FlechaMano — flecha dibujada

Coordenadas en % del cuadro. Típica: apuntar al botón al final.

```tsx
<FlechaMano en="hoy" desdeXY={[50, 60]} hastaXY={[50, 80]} curva={0.3} />
```

## Sonido — efecto suelto

Cuando el sonido no va pegado a un elemento.

```tsx
<Sonido src="whoosh" en="hasta" volumen={0.4} />
```

---

## Estructura del archivo de un anuncio

```tsx
// ── a1-01 · "texto del beat"
//    palabras: A@0 los@5 cincuenta@9 …
const Beat01: React.FC = () => (<> … </>);

const escenas: Escenas = {
  "a1-01": Beat01,
};

export const anuncio: DefinicionAnuncio = {
  id: "a1",
  estilo: "vintage-50s",
  banner: "el gancho que se queda arriba",
  manifest: manifest as Manifest,
  palabras: palabras as unknown as Record<string, Palabra[]>,
  escenas,
  musica: { src: "musica/a1.mp3" },
};
```

Mantén el comentario `// ── <id del beat>` arriba de cada escena: `revisar_anuncio.py` lo usa
para saber a qué beat pertenece cada ancla.

## Composición del cuadro (dónde va cada cosa)

- **y = 2–8**: banner-gancho (lo pone el sistema solo, no lo toques).
- **y = 14–20**: etiqueta de contexto ("la historia de Rosa", "hoy").
- **y = 30–60**: la ilustración o la escena principal.
- **y = 68–80**: el titular grande.
- **y = 82–90**: la etiqueta de apoyo.
- Ancho útil real: **860 px** centrados (los bordes decorados se comen el resto).
