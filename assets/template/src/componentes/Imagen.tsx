/** Ilustración o foto ya recortada (PNG con transparencia) dentro de public/recortes/.
 *  Si todavía no existe, dibuja un marcador con el nombre del archivo: así puedes
 *  montar y revisar el anuncio completo antes de gastar en imágenes. */
import React from "react";
import { Img, staticFile } from "remotion";
import { ANTON } from "../fuentes";
import { useEstilo } from "../estilos";
import { rebote as flotar, temblor as vibrar } from "../movimiento";
import { Capa, type PropsCapa } from "./Capa";
import { useExiste } from "./existe";

export const Imagen: React.FC<
  PropsCapa & {
    /** Ruta dentro de public/, normalmente "recortes/algo.png". */
    src: string;
    alto?: number;
    ancho?: number;
    /** Vibración continua: "x" (nervios, estornudo) o "y" (peso, cansancio). */
    temblor?: "x" | "y";
    amplitud?: number;
    /** Flotación suave (objetos ligeros). */
    rebote?: boolean;
    sombra?: boolean;
    voltear?: boolean;
  }
> = ({ src, alto = 700, ancho, temblor, amplitud = 3, rebote, sombra = true, voltear, ...capa }) => {
  const e = useEstilo();
  const ruta = src.includes("/") ? src : `recortes/${src}`;
  const existe = useExiste(ruta);
  const continuo = (t: number) => {
    const partes: string[] = [];
    if (temblor) partes.push(vibrar(t, temblor, amplitud));
    if (rebote) partes.push(flotar(t));
    return partes.join(" ");
  };
  const filtro = sombra && e.recorte.sombra ? `drop-shadow(10px 13px 0 ${e.recorte.sombra})` : undefined;
  return (
    <Capa ancho={Math.max(1000, (ancho ?? alto) + 200)} continuo={continuo} {...capa}>
      {existe === null ? null : existe ? (
        <Img
          src={staticFile(ruta)}
          style={{
            height: alto,
            width: ancho ?? "auto",
            objectFit: "contain",
            filter: filtro,
            transform: voltear ? "scaleX(-1)" : undefined,
          }}
        />
      ) : (
        <Marcador ruta={ruta} alto={alto} ancho={ancho ?? Math.round(alto * 0.8)} />
      )}
    </Capa>
  );
};

const Marcador: React.FC<{ ruta: string; alto: number; ancho: number }> = ({ ruta, alto, ancho }) => {
  const e = useEstilo();
  return (
    <div
      style={{
        width: ancho,
        height: alto,
        border: `6px dashed ${e.acento}`,
        borderRadius: 24,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        padding: 24,
        color: e.acento,
        fontFamily: ANTON,
        fontSize: 34,
        textTransform: "uppercase",
        lineHeight: 1.1,
        opacity: 0.85,
      }}
    >
      falta
      <br />
      {ruta}
    </div>
  );
};
