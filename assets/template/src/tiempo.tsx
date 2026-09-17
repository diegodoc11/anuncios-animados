/** Motor de tiempos: todo entra EXACTAMENTE cuando se dice la palabra.
 *
 *  Cada beat trae la lista de palabras de su locución (src/data/<anuncio>.palabras.json,
 *  que escribe pipeline/transcribir_voz.py) con el frame en el que suena cada una.
 *  Los componentes reciben `en="palabra"` y calculan solo su frame de entrada.
 *
 *  Sintaxis de ancla:
 *    en="pañal"          → la primera vez que se dice "pañal"
 *    en="noche#2"        → la segunda vez
 *    en="dos años"       → grupo de palabras seguidas (usa el frame de la primera)
 *    en="gotitas+8"      → 8 frames después
 *    en="resto-4"        → 4 frames antes
 *    en={45}             → frame fijo (relativo al acto en el que está)
 */
import React, { createContext, useContext } from "react";
import { Sequence, useCurrentFrame, useVideoConfig } from "remotion";
import type { Direccion, Momento, Palabra } from "./tipos";
import { movimientoEntrada, movimientoSalida } from "./movimiento";

type Beat = { id: string; frames: number; palabras: Palabra[] };

const BeatCtx = createContext<Beat>({ id: "sin-beat", frames: 1, palabras: [] });
/** Frame (dentro del beat) en el que empieza el acto actual. */
const OrigenCtx = createContext<number>(0);

/** Frames que se adelanta cada entrada para que el gráfico llegue justo con la voz. */
export const ANTICIPO = 2;

export const normalizar = (s: string): string =>
  s
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "");

export const BeatProvider: React.FC<{ beat: Beat; children: React.ReactNode }> = ({ beat, children }) => (
  <BeatCtx.Provider value={beat}>
    <OrigenCtx.Provider value={0}>{children}</OrigenCtx.Provider>
  </BeatCtx.Provider>
);

export const useBeat = () => useContext(BeatCtx);

/** Frame absoluto (dentro del beat) en el que se dice un ancla. */
export const frameDeAncla = (beat: Beat, ancla: string): number => {
  const m = ancla.trim().match(/^(.*?)(?:#(\d+))?\s*([+-]\s*\d+)?$/);
  if (!m || !m[1]) {
    throw new Error(`[${beat.id}] Ancla vacía o inválida: "${ancla}"`);
  }
  const buscadas = m[1].split(/\s+/).map(normalizar).filter(Boolean);
  const cual = m[2] ? Number(m[2]) : 1;
  const desfase = m[3] ? Number(m[3].replace(/\s/g, "")) : 0;
  const oidas = beat.palabras.map(([p]) => normalizar(p));
  let encontradas = 0;
  for (let i = 0; i + buscadas.length <= oidas.length; i++) {
    if (buscadas.every((b, k) => oidas[i + k] === b)) {
      encontradas++;
      if (encontradas === cual) return beat.palabras[i][1] + desfase;
    }
  }
  throw new Error(
    `[${beat.id}] No encuentro la palabra "${m[1]}"${cual > 1 ? ` (aparición nº ${cual})` : ""} en la locución.\n` +
      `Palabras de este beat: ${beat.palabras.map(([p, f]) => `${p}@${f}`).join(" ")}\n` +
      `Usa una de esas palabras (tal como se oyó) o un número de frame.`,
  );
};

/** Frame de entrada RELATIVO al acto actual. */
export const useInicio = (en?: Momento, delay = 0): number => {
  const beat = useContext(BeatCtx);
  const origen = useContext(OrigenCtx);
  if (en === undefined || en === null) return Math.max(0, delay);
  if (typeof en === "number") return Math.max(0, en + delay);
  return Math.max(0, frameDeAncla(beat, en) - ANTICIPO - origen + delay);
};

/** Convierte un Momento a frame absoluto dentro del beat. */
const aAbsoluto = (beat: Beat, origen: number, m: Momento): number =>
  typeof m === "number" ? origen + m : Math.max(0, frameDeAncla(beat, m) - ANTICIPO);

/**
 * Acto: un tramo dentro del mismo beat (varias "escenas" seguidas mientras habla la voz).
 * Los hijos cuentan su tiempo desde el inicio del acto, así que `en="palabra"` y
 * `delay={n}` siguen funcionando igual dentro.
 */
export const Acto: React.FC<{
  desde?: Momento;
  hasta?: Momento;
  entra?: Direccion;
  sale?: Direccion;
  children: React.ReactNode;
}> = ({ desde = 0, hasta, entra = "no", sale = "no", children }) => {
  const beat = useContext(BeatCtx);
  const origen = useContext(OrigenCtx);
  const inicio = aAbsoluto(beat, origen, desde);
  const fin = hasta === undefined ? beat.frames : aAbsoluto(beat, origen, hasta);
  const duracion = Math.max(1, fin - inicio);
  return (
    <Sequence from={inicio - origen} durationInFrames={duracion} layout="none" name={`acto ${inicio}→${fin}`}>
      <OrigenCtx.Provider value={inicio}>
        <MovimientoActo duracion={duracion} entra={entra} sale={sale}>
          {children}
        </MovimientoActo>
      </OrigenCtx.Provider>
    </Sequence>
  );
};

const MovimientoActo: React.FC<{
  duracion: number;
  entra: Direccion;
  sale: Direccion;
  children: React.ReactNode;
}> = ({ duracion, entra, sale, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t1 = entra === "no" ? "" : movimientoEntrada(entra, frame, fps);
  const t2 = sale === "no" ? "" : movimientoSalida(sale, frame, duracion, fps);
  const transform = `${t1} ${t2}`.trim();
  if (!transform) return <>{children}</>;
  return <div style={{ position: "absolute", inset: 0, transform }}>{children}</div>;
};
