/** Trazos hechos a mano: tachón de marcador, círculo de boceto y flecha.
 *  Se dibujan solos (el trazo avanza), nunca aparecen de golpe con fundido. */
import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { useEstilo } from "../estilos";
import { useInicio } from "../tiempo";
import { Capa, type PropsCapa } from "./Capa";

const avance = (frame: number, inicio: number, duracion: number): number =>
  interpolate(frame - inicio, [0, duracion], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

/** Raya de marcador encima de una frase (lo que ya no sirve). */
export const Tachon: React.FC<
  PropsCapa & { ancho?: number; grosor?: number; color?: string; duracion?: number }
> = ({ ancho = 620, grosor = 18, color, duracion = 8, ...capa }) => {
  const e = useEstilo();
  const frame = useCurrentFrame();
  const inicio = useInicio(capa.en, capa.delay ?? 0);
  const p = avance(frame, inicio, duracion);
  const alto = grosor * 3;
  const d = `M ${grosor} ${alto / 2 + 3} C ${ancho * 0.3} ${alto / 2 - 6}, ${ancho * 0.62} ${alto / 2 + 7}, ${
    ancho - grosor
  } ${alto / 2 - 3}`;
  return (
    <Capa ancho={ancho + 120} desde="no" rotar={-2.5} {...capa}>
      <svg width={ancho} height={alto} viewBox={`0 0 ${ancho} ${alto}`} style={{ overflow: "visible" }}>
        <path
          d={d}
          fill="none"
          stroke={color ?? e.acento}
          strokeWidth={grosor}
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - p}
          opacity={0.93}
        />
      </svg>
    </Capa>
  );
};

const caminoCirculo = (w: number, h: number): string => {
  const pasos = 70;
  const vueltas = 1.12;
  const cx = w / 2;
  const cy = h / 2;
  let d = "";
  for (let i = 0; i <= pasos; i++) {
    const a = -Math.PI * 0.62 + Math.PI * 2 * vueltas * (i / pasos);
    const rx = (w / 2 - 8) * (1 + 0.035 * Math.sin(a * 3 + 1));
    const ry = (h / 2 - 8) * (1 + 0.045 * Math.sin(a * 2));
    const x = cx + rx * Math.cos(a) + (i / pasos) * 7;
    const y = cy + ry * Math.sin(a) - (i / pasos) * 5;
    d += `${i === 0 ? "M " : " L "}${x.toFixed(1)} ${y.toFixed(1)}`;
  }
  return d;
};

/** Círculo de lápiz alrededor de lo importante. */
export const CirculoBoceto: React.FC<
  PropsCapa & { ancho?: number; alto?: number; grosor?: number; color?: string; duracion?: number }
> = ({ ancho = 560, alto = 260, grosor = 10, color, duracion = 14, ...capa }) => {
  const e = useEstilo();
  const frame = useCurrentFrame();
  const inicio = useInicio(capa.en, capa.delay ?? 0);
  const p = avance(frame, inicio, duracion);
  return (
    <Capa ancho={ancho + 120} desde="no" rotar={-1.5} {...capa}>
      <svg width={ancho} height={alto} viewBox={`0 0 ${ancho} ${alto}`} style={{ overflow: "visible" }}>
        <path
          d={caminoCirculo(ancho, alto)}
          fill="none"
          stroke={color ?? e.acento}
          strokeWidth={grosor}
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - p}
        />
      </svg>
    </Capa>
  );
};

/** Flecha dibujada a mano de un punto a otro (coordenadas en % del cuadro). */
export const FlechaMano: React.FC<{
  desdeXY: [number, number];
  hastaXY: [number, number];
  curva?: number;
  grosor?: number;
  color?: string;
  duracion?: number;
  en?: PropsCapa["en"];
  delay?: number;
}> = ({ desdeXY, hastaXY, curva = 0.22, grosor = 11, color, duracion = 12, en, delay = 0 }) => {
  const e = useEstilo();
  const frame = useCurrentFrame();
  const inicio = useInicio(en, delay);
  const p = avance(frame, inicio, duracion);
  if (frame < inicio) return null;
  const x1 = (desdeXY[0] / 100) * 1080;
  const y1 = (desdeXY[1] / 100) * 1920;
  const x2 = (hastaXY[0] / 100) * 1080;
  const y2 = (hastaXY[1] / 100) * 1920;
  const dx = x2 - x1;
  const dy = y2 - y1;
  const largo = Math.hypot(dx, dy) || 1;
  const cx = (x1 + x2) / 2 + (-dy / largo) * largo * curva;
  const cy = (y1 + y2) / 2 + (dx / largo) * largo * curva;
  // Ángulo de llegada para la punta de la flecha.
  const ang = Math.atan2(y2 - cy, x2 - cx);
  const puntaA = [x2 - 42 * Math.cos(ang - 0.42), y2 - 42 * Math.sin(ang - 0.42)];
  const puntaB = [x2 - 42 * Math.cos(ang + 0.42), y2 - 42 * Math.sin(ang + 0.42)];
  const pPunta = interpolate(p, [0.75, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const c = color ?? e.acento;
  return (
    <AbsoluteFill>
      <svg width={1080} height={1920} viewBox="0 0 1080 1920">
        <path
          d={`M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`}
          fill="none"
          stroke={c}
          strokeWidth={grosor}
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - p}
        />
        <path
          d={`M ${puntaA[0]} ${puntaA[1]} L ${x2} ${y2} L ${puntaB[0]} ${puntaB[1]}`}
          fill="none"
          stroke={c}
          strokeWidth={grosor}
          strokeLinecap="round"
          strokeLinejoin="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - pPunta}
        />
      </svg>
    </AbsoluteFill>
  );
};
