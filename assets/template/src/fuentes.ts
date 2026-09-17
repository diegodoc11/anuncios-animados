/** Tipografías. El titular SIEMPRE es Anton (condensada): la regla de ancho
 *  (0.42 × tamaño por carácter) está calculada para ella. Cada estilo elige su
 *  fuente de etiqueta en src/estilos.json. */
import { loadFont as cargarAnton } from "@remotion/google-fonts/Anton";
import { loadFont as cargarOswald } from "@remotion/google-fonts/Oswald";
import { loadFont as cargarCourier } from "@remotion/google-fonts/CourierPrime";
import { loadFont as cargarCabin } from "@remotion/google-fonts/CabinSketch";
import { loadFont as cargarRighteous } from "@remotion/google-fonts/Righteous";
import { loadFont as cargarPlayfair } from "@remotion/google-fonts/PlayfairDisplaySC";
import { loadFont as cargarBangers } from "@remotion/google-fonts/Bangers";
import { loadFont as cargarBarlow } from "@remotion/google-fonts/BarlowCondensed";
import { loadFont as cargarShareTech } from "@remotion/google-fonts/ShareTechMono";
import { loadFont as cargarSpecialElite } from "@remotion/google-fonts/SpecialElite";
import { loadFont as cargarIMFell } from "@remotion/google-fonts/IMFellEnglishSC";

export const ANTON = cargarAnton("normal", { weights: ["400"], subsets: ["latin", "latin-ext"] }).fontFamily;

/** Factor de ancho de Anton en mayúsculas: ancho ≈ 0.42 × tamaño × nº de caracteres. */
export const FACTOR_ANTON = 0.42;

const ETIQUETAS: Record<string, () => string> = {
  Oswald: () => cargarOswald("normal", { weights: ["600"], subsets: ["latin", "latin-ext"] }).fontFamily,
  CourierPrime: () => cargarCourier("normal", { weights: ["700"], subsets: ["latin", "latin-ext"] }).fontFamily,
  CabinSketch: () => cargarCabin("normal", { weights: ["700"], subsets: ["latin"] }).fontFamily,
  Righteous: () => cargarRighteous("normal", { weights: ["400"], subsets: ["latin", "latin-ext"] }).fontFamily,
  PlayfairDisplaySC: () => cargarPlayfair("normal", { weights: ["700"], subsets: ["latin", "latin-ext"] }).fontFamily,
  Bangers: () => cargarBangers("normal", { weights: ["400"], subsets: ["latin", "latin-ext"] }).fontFamily,
  BarlowCondensed: () => cargarBarlow("normal", { weights: ["700"], subsets: ["latin", "latin-ext"] }).fontFamily,
  ShareTechMono: () => cargarShareTech("normal", { weights: ["400"], subsets: ["latin"] }).fontFamily,
  SpecialElite: () => cargarSpecialElite("normal", { weights: ["400"], subsets: ["latin"] }).fontFamily,
  IMFellEnglishSC: () => cargarIMFell("normal", { weights: ["400"], subsets: ["latin"] }).fontFamily,
};

const memoria: Record<string, string> = {};

/** Carga (una sola vez) la fuente de etiqueta que pide el estilo. */
export const fuenteEtiqueta = (nombre: string): string => {
  if (!memoria[nombre]) {
    const cargar = ETIQUETAS[nombre];
    memoria[nombre] = cargar ? cargar() : ANTON;
  }
  return memoria[nombre];
};
