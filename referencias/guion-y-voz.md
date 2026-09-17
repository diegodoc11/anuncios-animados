# Del guion a la voz

## Cómo se parte un guion en beats

Un beat = una idea = una frase que la voz dice de corrido. Entre 2 y 6 segundos
(unos 25–90 caracteres). Si una frase tiene dos ideas, pártela en dos beats: cada beat es una
escena distinta, y un anuncio que cambia de imagen cada 3 segundos retiene más.

Estructura que funciona en Meta:

1. **Gancho (beats 1–2)**: el problema o el resultado, dicho en la primera persona del cliente.
2. **Cuerpo**: qué intentó y no funcionó → qué descubrió → qué pasó después. Un beat por paso.
3. **Prueba**: números, tiempos, "después de la quinta sesión…".
4. **CTA (último beat)**: qué tiene que hacer y qué gana. Va con el `sfx="ding"` y una flecha.

El **banner-gancho** (arriba, todo el video) es la promesa en 34 caracteres o menos:
*"de 12 cafés al día a 11.200 al mes"*. Quien mira sin sonido tiene que entender la oferta.

## Cifras, símbolos y nombres

El pipeline convierte las cifras a palabras antes de mandarlas a la voz:

| En el guion | Lo que dice la voz |
|---|---|
| `58 años` | cincuenta y ocho años |
| `11.200` | once mil doscientos |
| `24 horas` | veinticuatro horas |
| `50%` | cincuenta por ciento |
| `2,5` | dos coma cinco |
| `21 años` | veintiún años |

Lo que **no** se convierte solo y hay que escribir a mano: `24/7` (escribe *veinticuatro siete*),
horas (`3:30` → *tres y media*), ordinales (`5ª` → *quinta*) y monedas (`$450` → *cuatrocientos
cincuenta dólares*, o *mil pesos*, según el país).

**Nombres de marca**: si la voz los lee mal, guarda cómo suenan.

```bash
python -X utf8 "<SKILL>/scripts/configurar.py" pronunciacion "Kie.ai" "Kaiei"
```

También se puede poner por guion:

```json
{"id": "a1", "pronunciacion": {"Emsella": "Emsela"}, "beats": [ … ]}
```

## Entonación encadenada

`gen_voz.py` manda cada beat con `previous_text` y `next_text`: el modelo sabe qué se dijo antes
y qué viene después, así la entonación se encadena en vez de reiniciarse en cada frase. Por eso
los beats se generan **todos del mismo guion** y no sueltos.

Ajustes de voz (en `perfil.json`, se cambian con `configurar.py voz`):

- `stability` 0.45: más bajo = más expresivo (y más impredecible); más alto = más plano.
- `similarity_boost` 0.8: qué tanto se parece a la voz original.
- `style` 0.35: cuánta interpretación mete. Para anuncios, entre 0.3 y 0.5.

## El ritmo (lo que separa un anuncio de un audiolibro)

`apretar_voz.py` hace tres cosas sobre cada clip:

1. corta el silencio del principio y del final,
2. acorta las pausas internas largas,
3. acelera 1.1x **sin cambiar el tono**.

El resultado típico: 21 segundos de locución quedan en 17. Si un beat queda tragado o se come
una palabra, ponle `"tempo": 1.0` a ese beat en el guion y vuelve a correr `apretar_voz.py`.

Los clips originales nunca se pierden: viven en `material/voz-original/`.

## La verificación que evita el ridículo

`transcribir_voz.py` escucha lo que quedó y lo compara con el guion palabra por palabra.
Si un beat sale por debajo del 93% te dice qué palabras no se oyeron. **Nunca sigas con un beat
en rojo**: el anuncio estaría diciendo algo distinto a lo aprobado.

De paso, deja los tiempos por palabra: eso es lo que hace que todo entre sincronizado.
Si mañana cambias la voz, vuelves a correr `apretar_voz.py` + `transcribir_voz.py` y el anuncio
completo se re-sincroniza solo, sin tocar el código.

## Cuánto cuesta

La voz se cobra por caracteres. `gen_voz.py` sin `--si` te dice exactamente cuántos vas a gastar
y cuántos te quedan en la cuenta. Un anuncio de 60 segundos ronda los 900 caracteres.
Los clips se guardan con su texto: si no cambia el texto, no se vuelve a gastar.
