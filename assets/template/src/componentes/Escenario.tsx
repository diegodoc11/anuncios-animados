/** El "set" donde pasa todo: fondo de color, textura del estilo, escenografía
 *  (el marco decorado de los bordes), viñeta y la deriva suave de cámara. */
import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { useEstilo } from "../estilos";
import type { Estilo } from "../tipos";
import { useExiste } from "./existe";

const svgFondo = (contenido: string, ancho = 600, alto = 600): string =>
  `url("data:image/svg+xml;utf8,${encodeURIComponent(
    `<svg xmlns='http://www.w3.org/2000/svg' width='${ancho}' height='${alto}'>${contenido}</svg>`,
  )}")`;

const ruido = (frecuencia: number, semilla: number, octavas = 2): string =>
  svgFondo(
    `<filter id='r'><feTurbulence type='fractalNoise' baseFrequency='${frecuencia}' numOctaves='${octavas}' seed='${semilla}' stitchTiles='stitch'/><feColorMatrix type='saturate' values='0'/></filter><rect width='100%' height='100%' filter='url(#r)'/>`,
  );

const guilloche = (color: string): string => {
  let lineas = "";
  for (let i = 0; i < 14; i++) {
    const y = 20 + i * 42;
    let d = `M 0 ${y}`;
    for (let x = 0; x <= 600; x += 20) {
      d += ` L ${x} ${(y + Math.sin((x / 600) * Math.PI * 4 + i * 0.7) * 16).toFixed(1)}`;
    }
    lineas += `<path d='${d}' fill='none' stroke='${color}' stroke-width='1.4' opacity='0.5'/>`;
  }
  return svgFondo(lineas);
};

const contornos = (color: string): string => {
  let capas = "";
  for (let i = 0; i < 7; i++) {
    const r = 60 + i * 34;
    let d = "";
    for (let a = 0; a <= 64; a++) {
      const ang = (a / 64) * Math.PI * 2;
      const rr = r * (1 + 0.12 * Math.sin(ang * 3 + i) + 0.06 * Math.cos(ang * 5));
      const x = 300 + rr * Math.cos(ang);
      const y = 300 + rr * Math.sin(ang) * 0.8;
      d += `${a === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)} `;
    }
    capas += `<path d='${d}Z' fill='none' stroke='${color}' stroke-width='1.6' opacity='0.55'/>`;
  }
  return svgFondo(capas);
};

const estiloDeTextura = (e: Estilo, frame: number): React.CSSProperties => {
  const base: React.CSSProperties = {
    opacity: e.texturaOpacidad,
    mixBlendMode: e.texturaMezcla as React.CSSProperties["mixBlendMode"],
  };
  switch (e.textura) {
    case "grano":
      return { ...base, backgroundImage: ruido(0.85, 3), backgroundSize: "600px 600px" };
    case "persianas":
      return {
        ...base,
        backgroundImage: `repeating-linear-gradient(-26deg, rgba(255,255,255,0.22) 0px, rgba(255,255,255,0.22) 46px, rgba(0,0,0,0) 46px, rgba(0,0,0,0) 132px), ${ruido(
          0.9,
          (frame % 3) + 1,
        )}`,
        backgroundSize: "auto, 600px 600px",
        filter: "blur(2px)",
      };
    case "tiza":
      return {
        ...base,
        backgroundImage: `radial-gradient(ellipse at 22% 28%, rgba(255,255,255,0.22), rgba(255,255,255,0) 55%), radial-gradient(ellipse at 76% 68%, rgba(255,255,255,0.18), rgba(255,255,255,0) 60%), ${ruido(
          0.6,
          7,
        )}`,
        backgroundSize: "auto, auto, 600px 600px",
      };
    case "lineas":
      return {
        ...base,
        backgroundImage:
          "repeating-linear-gradient(0deg, rgba(255,255,255,0.05) 0px, rgba(255,255,255,0.05) 2px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 7px)",
      };
    case "guilloche":
      return { ...base, backgroundImage: guilloche(e.tinta), backgroundSize: "600px 600px" };
    case "puntos":
      return {
        ...base,
        backgroundImage: `radial-gradient(circle, ${e.acento} 22%, rgba(0,0,0,0) 24%)`,
        backgroundSize: "26px 26px",
      };
    case "tejido":
      return {
        ...base,
        backgroundImage:
          "repeating-linear-gradient(0deg, rgba(0,0,0,0.05) 0px, rgba(0,0,0,0.05) 3px, rgba(0,0,0,0) 3px, rgba(0,0,0,0) 8px), repeating-linear-gradient(90deg, rgba(0,0,0,0.05) 0px, rgba(0,0,0,0.05) 3px, rgba(0,0,0,0) 3px, rgba(0,0,0,0) 8px)",
      };
    case "cuadricula":
      return {
        ...base,
        backgroundImage:
          "linear-gradient(rgba(255,255,255,0.10) 1px, rgba(0,0,0,0) 1px), linear-gradient(90deg, rgba(255,255,255,0.10) 1px, rgba(0,0,0,0) 1px), linear-gradient(rgba(255,255,255,0.18) 2px, rgba(0,0,0,0) 2px), linear-gradient(90deg, rgba(255,255,255,0.18) 2px, rgba(0,0,0,0) 2px)",
        backgroundSize: "48px 48px, 48px 48px, 240px 240px, 240px 240px",
      };
    case "papel":
      return {
        ...base,
        backgroundImage: `${ruido(0.02, 11, 3)}, ${ruido(0.9, 4)}`,
        backgroundSize: "600px 600px, 600px 600px",
      };
    case "contornos":
      return { ...base, backgroundImage: contornos(e.tinta), backgroundSize: "600px 600px" };
    default:
      return { display: "none" };
  }
};

export const Fondo: React.FC = () => {
  const e = useEstilo();
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{ background: `radial-gradient(ellipse at 50% 42%, ${e.fondo2} 0%, ${e.fondo} 72%)` }}
    >
      <AbsoluteFill style={estiloDeTextura(e, frame)} />
    </AbsoluteFill>
  );
};

/** Marco decorado. Usa la imagen de escenografía si existe; si no, dibuja uno propio. */
export const Marco: React.FC<{ src?: string }> = ({ src }) => {
  const e = useEstilo();
  const existe = useExiste(src);
  if (existe && src) {
    return (
      <AbsoluteFill>
        <Img src={staticFile(src)} style={{ width: 1080, height: 1920, objectFit: "cover" }} />
      </AbsoluteFill>
    );
  }
  return <MarcoDibujado color={e.marco.color} color2={e.marco.color2} />;
};

const MarcoDibujado: React.FC<{ color: string; color2: string }> = ({ color, color2 }) => (
  <AbsoluteFill>
    <svg width={1080} height={1920} viewBox="0 0 1080 1920">
      <rect x="0" y="0" width="1080" height="1920" fill="none" stroke={color} strokeWidth="56" />
      <rect x="66" y="66" width="948" height="1788" fill="none" stroke={color2} strokeWidth="6" />
      <rect x="82" y="82" width="916" height="1756" fill="none" stroke={color} strokeWidth="2" />
      {[
        [66, 66],
        [1014, 66],
        [66, 1854],
        [1014, 1854],
      ].map(([x, y], i) => (
        <g key={i} transform={`translate(${x} ${y}) rotate(45)`}>
          <rect x="-17" y="-17" width="34" height="34" fill={color2} stroke={color} strokeWidth="4" />
        </g>
      ))}
    </svg>
  </AbsoluteFill>
);

export const Vineta: React.FC = () => {
  const e = useEstilo();
  return (
    <AbsoluteFill
      style={{ background: `radial-gradient(ellipse at 50% 48%, rgba(0,0,0,0) 52%, ${e.vineta} 100%)` }}
    />
  );
};

/** Deriva de cámara: todo respira un poquito, nunca se queda congelado. */
export const Deriva: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const x = Math.sin(t * 0.55) * 7;
  const y = Math.cos(t * 0.42) * 9;
  const escala = 1.035 + Math.sin(t * 0.3) * 0.008;
  return (
    <AbsoluteFill
      style={{ transform: `translate(${x.toFixed(2)}px, ${y.toFixed(2)}px) scale(${escala.toFixed(4)})` }}
    >
      {children}
    </AbsoluteFill>
  );
};

/** Filtros SVG que usan algunos estilos (tiza). */
export const FiltrosSvg: React.FC = () => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <defs>
      <filter id="tiza">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n" />
        <feDisplacementMap in="SourceGraphic" in2="n" scale="4" xChannelSelector="R" yChannelSelector="G" />
      </filter>
    </defs>
  </svg>
);
