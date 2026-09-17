# Control de calidad antes de entregar

## 1. Revisión automática

```bash
python -X utf8 pipeline/revisar_anuncio.py a1
```

Detecta lo que rompe el render (una palabra mal escrita en un `en=`) y lo que se ve feo
(textos que no caben, archivos que faltan, música sin preparar).

## 2. Borrador a media resolución

```bash
npx remotion render src/index.ts a1 out/a1-borrador.mp4 --scale=0.5
```

A `--scale=0.5` el render es unas 3 veces más rápido y sirve perfecto para revisar tiempos y
composición. El final se hace una sola vez, al final.

## 3. Hoja de contacto (y mirarla de verdad)

```bash
python -X utf8 pipeline/hoja_frames.py out/a1-borrador.mp4 revision --anuncio a1
```

Saca 3 frames por beat (entrada, mitad y final), los numera y dibuja en rosado las **líneas del
ancho útil**. Abre las hojas y revisa, en este orden:

1. **Nada toca las líneas rosadas.** Si un titular las pasa, acórtalo o pártelo con `\n`.
   Recuerda: tamaño máximo ≈ 2050 / número de caracteres.
2. **El banner se lee completo** arriba, sin que nada se le monte encima.
3. **Cada imagen aparece cuando se nombra.** Si entra tarde, revisa el ancla.
4. **Ningún beat quedó vacío** ni con el marcador punteado de "falta imagen".
5. **No hay dos cosas encimadas.** Entre un titular (y≈72) y su etiqueta (y≈84) tiene que
   quedar aire.
6. **El texto se lee sobre el fondo.** En estilos oscuros, los titulares van claros; en los
   claros, oscuros. Si un recorte queda detrás del texto, súbelo o bájalo.

## 4. Verlo con sonido

Mira el borrador completo, con audio, una vez. Cosas que solo se detectan oyendo:

- una palabra tragada por el 1.1x (vuelve a `transcribir_voz.py`);
- la música tapando la voz (`preparar_musica.py … --debajo 18`);
- efectos de sonido repetidos demasiado seguido (quita alguno);
- silencios largos entre beats (baja el `--pad` de `apretar_voz.py`).

## 5. Aprobación del usuario

Muéstrale el borrador y la hoja de contacto. Pregunta concreto: *¿el gancho te suena?,
¿la voz es la que quieres?, ¿el CTA dice lo que tiene que decir?* No renderices el final hasta
que diga que sí: el final cuesta tiempo, no plata, pero su tiempo también vale.

## 6. Render final y entrega

```bash
npx remotion render src/index.ts a1 out/a1.mp4
python -X utf8 pipeline/finalizar.py out/a1.mp4
```

Entregas dos archivos:

- `out/a1-final.mp4` → el que se sube a Meta o TikTok. Audio a -14 LUFS con pico -1 dBTP:
  es el nivel que usan las plataformas, así que no te lo van a subir ni bajar.
- `out/a1-celular.mp4` → menos de 30 MB, para mandarlo por WhatsApp.

## Cosas que se olvidan siempre

- El primer segundo decide: que la primera imagen entre en el frame 0, no en el 20.
- El banner es el único texto que se ve el 100% del video. Si el banner no vende, el anuncio no vende.
- Si el anuncio pasa de 60 segundos, corta beats del medio (los del "intenté esto y aquello"),
  nunca el gancho ni el CTA.
- En Reels y Stories, la interfaz de la app tapa la parte de abajo: no pongas texto crítico
  por debajo de y=90.
