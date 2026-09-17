import React from "react";
import { Composition, Folder } from "remotion";
import { ANUNCIOS } from "./anuncios";
import { Anuncio, duracionDeAnuncio } from "./componentes/Anuncio";
import { IDS_DE_ESTILO } from "./estilos";

/** Vertical para Reels / Stories / TikTok. */
export const FPS = 30;
export const ANCHO = 1080;
export const ALTO = 1920;

export const RemotionRoot: React.FC = () => (
  <>
    {ANUNCIOS.map((def) => (
      <Composition
        key={def.id}
        id={def.id}
        component={Anuncio}
        durationInFrames={duracionDeAnuncio(def)}
        fps={FPS}
        width={ANCHO}
        height={ALTO}
        defaultProps={{ anuncioId: def.id }}
      />
    ))}
    {/* El mismo anuncio de ejemplo en los 10 estilos, para que el cliente elija mirando. */}
    <Folder name="muestras-de-estilo">
      {IDS_DE_ESTILO.map((idEstilo) => (
        <Composition
          key={idEstilo}
          id={`muestra-${idEstilo}`}
          component={Anuncio}
          durationInFrames={duracionDeAnuncio(ANUNCIOS[0])}
          fps={FPS}
          width={ANCHO}
          height={ALTO}
          defaultProps={{ anuncioId: ANUNCIOS[0].id, estiloId: idEstilo }}
        />
      ))}
    </Folder>
  </>
);
