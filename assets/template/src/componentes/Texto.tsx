/** Textos del anuncio: titular grande, etiqueta de papel, sello y número que sube.
 *  Todos se auto-ajustan para no salirse del marco (ancho útil 860 px). */
import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { ANTON, FACTOR_ANTON, fuenteEtiqueta } from "../fuentes";
import { useEstilo } from "../estilos";
import type { Estilo } from "../tipos";
import { useInicio } from "../tiempo";
import { Capa, textoDe, type PropsCapa } from "./Capa";

/** Ancho libre entre los bordes de la escenografía. */
export const ANCHO_UTIL = 860;

const efectoDelTitular = (e: Estilo, color: string): React.CSSProperties => {
  switch (e.efectoTitular) {
    case "sombra-dura":
      return { textShadow: `0.045em 0.05em 0 ${e.sombraTitular ?? e.acento}` };
    case "brillo":
      return { textShadow: `0 0 0.04em #ffffff, 0 0 0.22em ${color}, 0 0 0.55em ${color}` };
    case "tiza":
      return { filter: "url(#tiza)", textShadow: "0 0 0.02em rgba(255,255,255,0.55)" };
    case "comic":
      return {
        WebkitTextStrokeWidth: "0.035em",
        WebkitTextStrokeColor: e.tinta,
        textShadow: `0.05em 0.055em 0 ${e.tinta}`,
      };
    case "grabado":
      return {
        textShadow: "0.012em 0.012em 0 rgba(255,255,255,0.75), -0.012em -0.012em 0 rgba(0,0,0,0.30)",
        letterSpacing: "0.02em",
      };
    default:
      return {};
  }
};

/** Tamaño que cabe: ancho ≈ 0.42 × tamaño × caracteres de la línea más larga.
 *  Se deja un 5% de aire para que el texto no quede pegado al borde decorado. */
export const tamanoQueCabe = (texto: string, pedido: number, anchoUtil = ANCHO_UTIL): number => {
  const lineas = texto.split("\n");
  const largo = Math.max(1, ...lineas.map((l) => l.trim().length));
  return Math.max(24, Math.min(pedido, Math.floor((anchoUtil * 0.95) / (FACTOR_ANTON * largo))));
};

export type PropsTitular = PropsCapa & {
  children: React.ReactNode;
  size?: number;
  color?: string;
  /** Usa el color de acento del estilo. */
  acento?: boolean;
  anchoUtil?: number;
  interlinea?: number;
};

/** Palabra o frase grande, en mayúsculas condensadas. Usa "\n" para partir líneas. */
export const Titular: React.FC<PropsTitular> = ({
  children,
  size = 140,
  color,
  acento,
  anchoUtil = ANCHO_UTIL,
  interlinea = 0.95,
  ...capa
}) => {
  const e = useEstilo();
  const texto = textoDe(children);
  const tam = tamanoQueCabe(texto, size, anchoUtil);
  const c = color ?? (acento ? e.acento : e.efectoTitular === "comic" ? "#ffffff" : e.tinta);
  return (
    <Capa ancho={anchoUtil + 180} desde="abajo" {...capa}>
      <div
        style={{
          fontFamily: ANTON,
          fontSize: tam,
          lineHeight: interlinea,
          color: c,
          textTransform: "uppercase",
          textAlign: "center",
          whiteSpace: "pre-line",
          ...efectoDelTitular(e, c),
        }}
      >
        {texto}
      </div>
    </Capa>
  );
};

export type PropsEtiqueta = PropsCapa & {
  children: React.ReactNode;
  size?: number;
  color?: string;
  fondo?: string;
  sombra?: string;
  anchoUtil?: number;
};

/** Frase de apoyo sobre un papelito. Se parte sola en varias líneas si es larga. */
export const Etiqueta: React.FC<PropsEtiqueta> = ({
  children,
  size = 52,
  color,
  fondo,
  sombra,
  anchoUtil = ANCHO_UTIL,
  ...capa
}) => {
  const e = useEstilo();
  const sombraFinal = sombra ?? e.etiqueta.sombra;
  return (
    <Capa ancho={anchoUtil + 180} desde="izquierda" rotar={-1.2} {...capa}>
      <div
        style={{
          fontFamily: fuenteEtiqueta(e.fuenteEtiqueta),
          fontSize: size,
          lineHeight: 1.15,
          textTransform: "uppercase",
          color: color ?? e.etiqueta.tinta,
          background: fondo ?? e.etiqueta.fondo,
          border: e.etiqueta.borde ?? undefined,
          padding: "0.24em 0.5em",
          maxWidth: anchoUtil,
          textAlign: "center",
          letterSpacing: "0.02em",
          boxShadow: sombraFinal === "transparent" ? undefined : `0.13em 0.14em 0 ${sombraFinal}`,
          textShadow: e.efectoTitular === "brillo" ? `0 0 0.35em ${e.acento2}` : undefined,
        }}
      >
        {children}
      </div>
    </Capa>
  );
};

const MASCARA_TINTA =
  "url(\"data:image/svg+xml;utf8," +
  encodeURIComponent(
    "<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='m'><feTurbulence type='fractalNoise' baseFrequency='0.7' numOctaves='2' seed='5'/><feColorMatrix type='matrix' values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0.85 0 0 0 0.5'/></filter><rect width='100%' height='100%' filter='url(#m)'/></svg>",
  ) +
  "\")";

/** Sello de caucho: entra de golpe, con borde y tinta gastada. */
export const Sello: React.FC<PropsCapa & { children: React.ReactNode; size?: number; color?: string }> = ({
  children,
  size = 68,
  color,
  ...capa
}) => {
  const e = useEstilo();
  const c = color ?? e.acento;
  const texto = textoDe(children);
  const tam = tamanoQueCabe(texto, size, ANCHO_UTIL - 120);
  return (
    <Capa ancho={ANCHO_UTIL + 180} desde="sello" rotar={-7} {...capa}>
      <div
        style={{
          fontFamily: ANTON,
          fontSize: tam,
          color: c,
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          padding: "0.14em 0.34em",
          border: `0.075em solid ${c}`,
          borderRadius: "0.08em",
          boxShadow: `inset 0 0 0 0.025em ${c}`,
          textAlign: "center",
          WebkitMaskImage: MASCARA_TINTA,
          maskImage: MASCARA_TINTA,
          WebkitMaskSize: "160px 160px",
          maskSize: "160px 160px",
        }}
      >
        {texto}
      </div>
    </Capa>
  );
};

/** 11200 → "11.200" (formato de Colombia: punto para miles, coma para decimales). */
export const formatearNumero = (valor: number, decimales = 0): string => {
  const fijo = Math.abs(valor).toFixed(decimales);
  const [entero, decimal] = fijo.split(".");
  const conPuntos = entero.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  const signo = valor < 0 ? "-" : "";
  return signo + conPuntos + (decimal ? `,${decimal}` : "");
};

/** Número que sube desde 0 (ventas, clientes, pesos…). */
export const Contador: React.FC<
  PropsCapa & {
    hasta: number;
    inicia?: number;
    duracion?: number;
    decimales?: number;
    prefijo?: string;
    sufijo?: string;
    size?: number;
    color?: string;
    acento?: boolean;
  }
> = ({
  hasta,
  inicia = 0,
  duracion = 28,
  decimales = 0,
  prefijo = "",
  sufijo = "",
  size = 170,
  color,
  acento,
  ...capa
}) => {
  const e = useEstilo();
  const frame = useCurrentFrame();
  const inicio = useInicio(capa.en, capa.delay ?? 0);
  const textoFinal = `${prefijo}${formatearNumero(hasta, decimales)}${sufijo}`;
  const tam = tamanoQueCabe(textoFinal, size);
  const c = color ?? (acento ? e.acento : e.efectoTitular === "comic" ? "#ffffff" : e.tinta);
  const p = interpolate(frame - inicio, [0, duracion], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const valor = inicia + (hasta - inicia) * p;
  return (
    <Capa ancho={ANCHO_UTIL + 180} desde="abajo" {...capa}>
      <div
        style={{
          fontFamily: ANTON,
          fontSize: tam,
          color: c,
          lineHeight: 1,
          textTransform: "uppercase",
          textAlign: "center",
          fontVariantNumeric: "tabular-nums",
          ...efectoDelTitular(e, c),
        }}
      >
        {prefijo}
        {formatearNumero(valor, decimales)}
        {sufijo}
      </div>
    </Capa>
  );
};
