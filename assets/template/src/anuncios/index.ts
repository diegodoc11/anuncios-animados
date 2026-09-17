/** Registro de anuncios. Cada anuncio nuevo se agrega aquí (una línea de import y otra en la lista).
 *  pipeline/esqueleto_anuncio.py lo hace solo. */
import type { DefinicionAnuncio } from "../tipos";
import { anuncio as ejemplo } from "./ejemplo";

export const ANUNCIOS: DefinicionAnuncio[] = [ejemplo];

export const anuncioPorId = (id: string): DefinicionAnuncio => {
  const def = ANUNCIOS.find((a) => a.id === id);
  if (!def) {
    throw new Error(`No existe el anuncio "${id}". Registrados: ${ANUNCIOS.map((a) => a.id).join(", ")}`);
  }
  return def;
};
