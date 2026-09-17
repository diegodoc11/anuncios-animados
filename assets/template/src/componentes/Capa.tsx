/** Capa: coloca cualquier cosa en el cuadro (x, y en % del video), la hace entrar
 *  deslizándose y, si quieres, dispara un efecto de sonido en ese mismo frame. */
import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { useInicio } from "../tiempo";
import { movimientoEntrada } from "../movimiento";
import type { Direccion, Momento } from "../tipos";
import { Sonido } from "./Sonido";

export type PropsCapa = {
  /** Centro horizontal, 0–100 (% del ancho). */
  x?: number;
  /** Centro vertical, 0–100 (% del alto). */
  y?: number;
  /** Palabra de la locución en la que entra. */
  en?: Momento;
  /** Frames de retraso (sumados al ancla, o desde el inicio del acto si no hay ancla). */
  delay?: number;
  /** Por dónde entra. Nunca usamos fundidos. */
  desde?: Direccion;
  rotar?: number;
  escala?: number;
  /** Efecto de sonido que suena al entrar: "whoosh" | "pop" | "click" | "golpe" | "papel" | "ding". */
  sfx?: string;
  sfxVolumen?: number;
  zIndex?: number;
};

export const Capa: React.FC<
  PropsCapa & {
    /** Ancho de la caja invisible que centra el contenido. */
    ancho?: number;
    /** Movimiento continuo extra (temblor, flotación…). Recibe los frames desde la entrada. */
    continuo?: (t: number) => string;
    children: React.ReactNode;
  }
> = ({
  x = 50,
  y = 50,
  en,
  delay = 0,
  desde = "abajo",
  rotar = 0,
  escala = 1,
  sfx,
  sfxVolumen = 0.5,
  zIndex,
  ancho = 1000,
  continuo,
  children,
}) => {
  const inicio = useInicio(en, delay);
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame - inicio;
  const entrada = movimientoEntrada(desde, t, fps);
  const extra = continuo && t >= 0 ? continuo(t) : "";
  return (
    <>
      {t >= 0 ? (
        <div
          style={{
            position: "absolute",
            left: `${x}%`,
            top: `${y}%`,
            width: ancho,
            marginLeft: -ancho / 2,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transform: `translateY(-50%) ${entrada} rotate(${rotar}deg) scale(${escala}) ${extra}`,
            zIndex,
          }}
        >
          {children}
        </div>
      ) : null}
      {sfx ? <Sonido src={sfx} en={inicio} volumen={sfxVolumen} /> : null}
    </>
  );
};

/** Saca el texto plano de unos children (para medir cuánto ocupa). */
export const textoDe = (n: React.ReactNode): string => {
  if (n === null || n === undefined || typeof n === "boolean") return "";
  if (typeof n === "string") return n;
  if (typeof n === "number") return String(n);
  if (Array.isArray(n)) return n.map(textoDe).join("");
  return "";
};
