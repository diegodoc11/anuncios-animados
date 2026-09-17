import type React from "react";

/** Una palabra oída en la locución y el frame (dentro del beat) en el que se dice. */
export type Palabra = [string, number];

/** Momento de entrada: número de frames o una palabra de la locución ("pañal", "noche#2", "gotitas+6"). */
export type Momento = string | number;

export type Direccion = "izquierda" | "derecha" | "arriba" | "abajo" | "centro" | "sello" | "no";

export type BeatManifest = {
  id: string;
  texto: string;
  frames: number;
  segundos?: number;
  /** Ruta dentro de public/ del clip de voz. Si falta, el beat va mudo. */
  voz?: string;
};

export type Manifest = {
  fps: number;
  pad?: number;
  tempo?: number;
  estimado?: boolean;
  beats: BeatManifest[];
};

export type Escenas = Record<string, React.FC>;

export type DefinicionAnuncio = {
  /** Id de la composición en Remotion (solo letras, números y guiones). */
  id: string;
  /** Clave de src/estilos.json */
  estilo: string;
  /** Texto del banner permanente de arriba. */
  banner?: string;
  manifest: Manifest;
  palabras: Record<string, Palabra[]>;
  escenas: Escenas;
  /** Música ya preparada por pipeline/preparar_musica.py (ruta dentro de public/). */
  musica?: { src: string; volumen?: number };
  /** Escenografía propia (ruta dentro de public/). Por defecto: escenografia/<estilo>.png */
  escenografia?: string;
};

export type Estilo = {
  nombre: string;
  paraQue: string;
  oscuro: boolean;
  fondo: string;
  fondo2: string;
  tinta: string;
  acento: string;
  acento2: string;
  sombraTitular: string | null;
  efectoTitular: "ninguno" | "sombra-dura" | "brillo" | "tiza" | "comic" | "grabado";
  fuenteEtiqueta: string;
  etiqueta: { fondo: string; tinta: string; sombra: string; borde: string | null };
  banner: { fondo: string; tinta: string; sombra: string; forma: "cinta" | "tubo" | "bloque" };
  textura: "grano" | "persianas" | "tiza" | "lineas" | "guilloche" | "puntos" | "tejido" | "cuadricula" | "papel" | "contornos" | "ninguna";
  texturaOpacidad: number;
  texturaMezcla: string;
  vineta: string;
  marco: { color: string; color2: string };
  recorte: {
    modo: "chroma" | "luz";
    fondoPrompt: string;
    borde: string | null;
    grosorBorde: number;
    sombra: string | null;
  };
  promptImagen: string;
  promptEscenografia: string;
  musica: string;
  foto: string;
};
