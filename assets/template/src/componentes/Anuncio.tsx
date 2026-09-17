/** Arma el anuncio completo: fondo + escenas beat por beat + voz + música + marco + banner. */
import React from "react";
import { AbsoluteFill, Html5Audio, Sequence, staticFile, useVideoConfig } from "remotion";
import { EstiloCtx, estiloPorId } from "../estilos";
import { BeatProvider } from "../tiempo";
import type { BeatManifest, DefinicionAnuncio } from "../tipos";
import { anuncioPorId } from "../anuncios";
import { Banner } from "./Banner";
import { Deriva, FiltrosSvg, Fondo, Marco, Vineta } from "./Escenario";
import { Etiqueta } from "./Texto";
import { useExiste } from "./existe";

export const duracionDeAnuncio = (def: DefinicionAnuncio): number =>
  Math.max(1, def.manifest.beats.reduce((suma, b) => suma + b.frames, 0));

const EscenaPendiente: React.FC<{ beat: BeatManifest }> = ({ beat }) => (
  <Etiqueta y={50} size={40} desde="abajo">
    {beat.id}: {beat.texto}
  </Etiqueta>
);

const Musica: React.FC<{ src: string; volumen: number }> = ({ src, volumen }) => {
  const { durationInFrames, fps } = useVideoConfig();
  const existe = useExiste(src);
  if (!existe) return null;
  return (
    <Html5Audio
      src={staticFile(src)}
      volume={(f) =>
        volumen *
        Math.min(1, Math.max(0, f) / (fps * 0.8)) *
        Math.min(1, Math.max(0, durationInFrames - f) / (fps * 1.6))
      }
    />
  );
};

export const Anuncio: React.FC<{ anuncioId: string; estiloId?: string }> = ({ anuncioId, estiloId }) => {
  const def = anuncioPorId(anuncioId);
  const idEstilo = estiloId ?? def.estilo;
  const estilo = estiloPorId(idEstilo);
  const escenografia = def.escenografia ?? `escenografia/${idEstilo}.png`;

  let cursor = 0;
  const bloques = def.manifest.beats.map((beat) => {
    const desde = cursor;
    cursor += beat.frames;
    return { beat, desde };
  });

  return (
    <EstiloCtx.Provider value={estilo}>
      <AbsoluteFill style={{ backgroundColor: estilo.fondo }}>
        <FiltrosSvg />
        <Deriva>
          <Fondo />
          {bloques.map(({ beat, desde }) => {
            const Escena = def.escenas[beat.id];
            return (
              <Sequence key={beat.id} from={desde} durationInFrames={beat.frames} name={beat.id}>
                <BeatProvider
                  beat={{ id: beat.id, frames: beat.frames, palabras: def.palabras[beat.id] ?? [] }}
                >
                  {Escena ? <Escena /> : <EscenaPendiente beat={beat} />}
                </BeatProvider>
              </Sequence>
            );
          })}
        </Deriva>
        <Marco src={escenografia} />
        <Vineta />
        {def.banner ? <Banner texto={def.banner} /> : null}
        {bloques.map(({ beat, desde }) =>
          beat.voz ? (
            <Sequence
              key={`voz-${beat.id}`}
              from={desde}
              durationInFrames={beat.frames}
              layout="none"
              name={`voz ${beat.id}`}
            >
              <Html5Audio src={staticFile(beat.voz)} />
            </Sequence>
          ) : null,
        )}
        {def.musica ? <Musica src={def.musica.src} volumen={def.musica.volumen ?? 1} /> : null}
      </AbsoluteFill>
    </EstiloCtx.Provider>
  );
};
