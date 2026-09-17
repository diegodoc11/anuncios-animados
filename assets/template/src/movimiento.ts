/** Entradas y salidas. Regla de la casa: NADA entra con fundido (opacidad).
 *  Todo entra deslizándose desde fuera del cuadro, o con un golpe de sello. */
import { Easing, interpolate, spring } from "remotion";
import type { Direccion } from "./tipos";

const FUERA_X = 1250;
const FUERA_Y = 1500;

export const movimientoEntrada = (desde: Direccion, t: number, fps: number): string => {
  if (desde === "no" || t < 0) return "";
  const s = spring({ frame: t, fps, config: { damping: 15, stiffness: 150, mass: 0.7 } });
  const resto = 1 - s;
  switch (desde) {
    case "izquierda":
      return `translateX(${(-FUERA_X * resto).toFixed(2)}px)`;
    case "derecha":
      return `translateX(${(FUERA_X * resto).toFixed(2)}px)`;
    case "arriba":
      return `translateY(${(-FUERA_Y * resto).toFixed(2)}px)`;
    case "abajo":
      return `translateY(${(FUERA_Y * resto).toFixed(2)}px)`;
    case "centro":
      return `scale(${s.toFixed(3)})`;
    case "sello": {
      const golpe = spring({ frame: t, fps, config: { damping: 12, stiffness: 280, mass: 0.6 } });
      return `scale(${(2.3 - 1.3 * golpe).toFixed(3)})`;
    }
    default:
      return "";
  }
};

/** Salida: se va del cuadro en los últimos frames del acto. */
export const movimientoSalida = (hacia: Direccion, frame: number, duracion: number, fps: number): string => {
  const largo = Math.min(9, Math.max(5, Math.round(fps / 4)));
  const inicio = duracion - largo;
  if (hacia === "no" || frame < inicio) return "";
  const p = interpolate(frame, [inicio, duracion], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.cubic),
  });
  switch (hacia) {
    case "izquierda":
      return `translateX(${(-FUERA_X * p).toFixed(2)}px)`;
    case "derecha":
      return `translateX(${(FUERA_X * p).toFixed(2)}px)`;
    case "arriba":
      return `translateY(${(-FUERA_Y * p).toFixed(2)}px)`;
    case "abajo":
      return `translateY(${(FUERA_Y * p).toFixed(2)}px)`;
    case "centro":
    case "sello":
      return `scale(${(1 - p).toFixed(3)})`;
    default:
      return "";
  }
};

/** Vibración continua (para objetos con tensión: estornudo, peso, alarma). */
export const temblor = (t: number, eje: "x" | "y", amplitud: number): string => {
  const d = Math.sin(t * 1.9) * amplitud;
  return eje === "x" ? `translateX(${d.toFixed(2)}px)` : `translateY(${d.toFixed(2)}px)`;
};

/** Flotación suave (para objetos ligeros: gotas, globos, celular). */
export const rebote = (t: number, amplitud = 9): string => `translateY(${(Math.sin(t / 8) * amplitud).toFixed(2)}px)`;
