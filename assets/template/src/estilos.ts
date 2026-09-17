import { createContext, useContext } from "react";
import datos from "./estilos.json";
import type { Estilo } from "./tipos";

export const ESTILOS = datos as unknown as Record<string, Estilo>;
export const IDS_DE_ESTILO = Object.keys(ESTILOS);

export const estiloPorId = (id: string): Estilo => {
  const e = ESTILOS[id];
  if (!e) {
    throw new Error(`No existe el estilo "${id}". Estilos disponibles: ${IDS_DE_ESTILO.join(", ")}`);
  }
  return e;
};

export const EstiloCtx = createContext<Estilo>(ESTILOS["vintage-50s"]);
export const useEstilo = (): Estilo => useContext(EstiloCtx);
