/** Efecto de sonido. Los .wav los crea pipeline/crear_sfx.py con ffmpeg (son tuyos,
 *  no hay audio de terceros). Si el archivo no está, el render sigue sin sonido. */
import React from "react";
import { Html5Audio, Sequence, staticFile } from "remotion";
import { useInicio } from "../tiempo";
import type { Momento } from "../tipos";
import { useExiste } from "./existe";

export const rutaSfx = (src: string): string => (src.includes("/") || src.includes(".") ? src : `sfx/${src}.wav`);

export const Sonido: React.FC<{ src: string; en?: Momento; delay?: number; volumen?: number }> = ({
  src,
  en,
  delay = 0,
  volumen = 0.5,
}) => {
  const inicio = useInicio(en, delay);
  const ruta = rutaSfx(src);
  const existe = useExiste(ruta);
  if (!existe) return null;
  return (
    <Sequence from={inicio} layout="none" name={`sfx ${src}`}>
      <Html5Audio src={staticFile(ruta)} volume={volumen} />
    </Sequence>
  );
};
