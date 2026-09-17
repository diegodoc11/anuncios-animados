/* ANUNCIO DE EJEMPLO — "Don Julio" (historia inventada, sirve de plantilla)
 *
 *  Cómo se lee este archivo:
 *   · una función por beat, con el mismo id del guion (guiones/ejemplo.json);
 *   · `en="palabra"` = eso entra justo cuando la voz dice esa palabra;
 *   · `<Acto>` = varios momentos dentro del mismo beat;
 *   · los tiempos salen de src/data/ejemplo.palabras.json (aquí son estimados,
 *     porque este ejemplo no tiene locución; con voz real los reescribe
 *     pipeline/transcribir_voz.py y todo se re-sincroniza solo).
 */
import React from "react";
import {
  Acto,
  CirculoBoceto,
  Contador,
  Etiqueta,
  FlechaMano,
  Imagen,
  Sello,
  Tachon,
  Titular,
} from "../componentes/publico";
import manifest from "../data/ejemplo.manifest.json";
import palabras from "../data/ejemplo.palabras.json";
import type { DefinicionAnuncio, Escenas, Manifest, Palabra } from "../tipos";

// ── ejemplo-01 · "Don Julio vendía 12 cafés al día en la esquina de su barrio."
const Beat01: React.FC = () => (
  <>
    <Etiqueta y={16} size={44} desde="arriba">
      la historia de don julio
    </Etiqueta>
    <Imagen src="recortes/julio-carrito.png" y={44} alto={700} desde="abajo" sfx="whoosh" />
    <Contador en="doce" hasta={12} sufijo=" cafés" y={74} size={150} sfx="pop" />
    <Etiqueta en="esquina" y={84}>
      al día, en la esquina del barrio
    </Etiqueta>
  </>
);

// ── ejemplo-02 · "Probó volantes, probó descuentos, probó regalar galletas. Nada movió la aguja."
const Beat02: React.FC = () => (
  <>
    <Acto hasta="Nada" sale="izquierda">
      <Titular en="volantes" y={32} size={120} desde="izquierda" sfx="whoosh">
        volantes
      </Titular>
      <Titular en="descuentos" y={47} size={120} desde="derecha" sfx="whoosh">
        descuentos
      </Titular>
      <Titular en="galletas" y={62} size={120} desde="izquierda" sfx="whoosh">
        galletas gratis
      </Titular>
      <Tachon en="galletas+14" y={32} ancho={560} />
      <Tachon en="galletas+18" y={47} ancho={700} />
      <Tachon en="galletas+22" y={62} ancho={760} sfx="papel" />
    </Acto>
    <Acto desde="Nada" entra="derecha">
      <Titular y={44} size={210} acento>
        nada
      </Titular>
      <Sello en="aguja" y={62} sfx="golpe">
        cero movimiento
      </Sello>
    </Acto>
  </>
);

// ── ejemplo-03 · "Hasta que grabó un video de 30 segundos mostrando cómo tuesta su café."
const Beat03: React.FC = () => (
  <>
    <Imagen src="recortes/celular-video.png" y={42} alto={620} desde="derecha" rebote sfx="whoosh" />
    <Titular en="video" y={74} size={150}>
      un video
    </Titular>
    <Etiqueta en="segundos" y={85}>
      de 30 segundos tostando su café
    </Etiqueta>
    <CirculoBoceto en="segundos+6" y={85} ancho={760} alto={140} />
  </>
);

// ── ejemplo-04 · "Ese mes vendió 11.200 cafés con el mismo local y el mismo café."
const Beat04: React.FC = () => (
  <>
    <Acto hasta="once" sale="arriba">
      <Titular y={40} size={130} desde="izquierda">
        12 cafés al día
      </Titular>
      <Tachon delay={10} y={40} ancho={700} sfx="papel" />
    </Acto>
    <Acto desde="once">
      <Etiqueta y={30} size={46} desde="arriba">
        ese mes vendió
      </Etiqueta>
      <Contador hasta={11200} sufijo=" cafés" y={46} size={190} duracion={26} sfx="pop" />
      <Etiqueta en="mismo#2" y={64}>
        mismo local, mismo café
      </Etiqueta>
      <Sello en="café" y={78} sfx="golpe">
        solo cambió el anuncio
      </Sello>
    </Acto>
  </>
);

// ── ejemplo-05 · "Toca el botón y arma tu primer anuncio animado hoy mismo."
const Beat05: React.FC = () => (
  <>
    <Titular y={38} size={150} desde="abajo" sfx="ding">
      toca el botón
    </Titular>
    <Etiqueta en="anuncio" y={52}>
      y arma tu primer anuncio animado hoy
    </Etiqueta>
    <FlechaMano en="hoy" desdeXY={[50, 60]} hastaXY={[50, 80]} curva={0.3} />
  </>
);

const escenas: Escenas = {
  "ejemplo-01": Beat01,
  "ejemplo-02": Beat02,
  "ejemplo-03": Beat03,
  "ejemplo-04": Beat04,
  "ejemplo-05": Beat05,
};

export const anuncio: DefinicionAnuncio = {
  id: "ejemplo",
  estilo: "vintage-50s",
  banner: "de 12 cafés al día a 11.200 al mes",
  manifest: manifest as Manifest,
  palabras: palabras as unknown as Record<string, Palabra[]>,
  escenas,
  musica: { src: "musica/ejemplo.mp3", volumen: 1 },
};
