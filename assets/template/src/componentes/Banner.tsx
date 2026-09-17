/** Banner-gancho permanente de arriba: la promesa del anuncio, visible los 100% del video
 *  (quien lo ve en silencio igual entiende la oferta). */
import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ANTON, FACTOR_ANTON } from "../fuentes";
import { useEstilo } from "../estilos";

const ANCHO_BANNER = 940;

export const Banner: React.FC<{ texto: string; y?: number }> = ({ texto, y = 44 }) => {
  const e = useEstilo();
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const entrada = spring({ frame, fps, config: { damping: 16, stiffness: 130, mass: 0.8 } });
  const tam = Math.max(26, Math.min(58, Math.floor(ANCHO_BANNER / (FACTOR_ANTON * Math.max(1, texto.length)))));
  const b = e.banner;

  const comun: React.CSSProperties = {
    fontFamily: ANTON,
    fontSize: tam,
    color: b.tinta,
    textTransform: "uppercase",
    letterSpacing: "0.03em",
    padding: "0.24em 0.7em",
    textAlign: "center",
    maxWidth: ANCHO_BANNER,
  };

  const porForma: React.CSSProperties =
    b.forma === "tubo"
      ? {
          background: b.fondo,
          border: `4px solid ${b.sombra}`,
          borderRadius: 16,
          boxShadow: `0 0 22px ${b.sombra}, inset 0 0 18px ${b.sombra}`,
          textShadow: `0 0 10px ${b.sombra}, 0 0 26px ${b.sombra}`,
        }
      : b.forma === "bloque"
        ? {
            background: b.fondo,
            border: `3px solid ${b.tinta}`,
            outline: `2px solid ${b.sombra}`,
            outlineOffset: 6,
          }
        : {
            background: b.fondo,
            boxShadow: `9px 9px 0 ${b.sombra}`,
          };

  return (
    <div
      style={{
        position: "absolute",
        top: y,
        left: 0,
        width: 1080,
        display: "flex",
        justifyContent: "center",
        transform: `translateY(${((entrada - 1) * 220).toFixed(2)}px) rotate(${b.forma === "cinta" ? -1 : 0}deg)`,
        zIndex: 20,
      }}
    >
      <div style={{ ...comun, ...porForma }}>{texto}</div>
    </div>
  );
};
