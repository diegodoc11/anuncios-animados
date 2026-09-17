/** ¿Ese archivo está realmente en public/?
 *  Sirve para que el anuncio se pueda ver aunque todavía falten imágenes, música o efectos:
 *  lo que falta se dibuja como un marcador (o simplemente no suena) en vez de romper el render. */
import { useEffect, useState } from "react";
import { continueRender, delayRender, staticFile } from "remotion";

const memoria = new Map<string, Promise<boolean>>();

const consultar = (ruta: string): Promise<boolean> => {
  const guardada = memoria.get(ruta);
  if (guardada) return guardada;
  const promesa = fetch(staticFile(ruta), { method: "HEAD" })
    .then((r) => {
      const tipo = r.headers.get("content-type") ?? "";
      return r.ok && !tipo.includes("text/html");
    })
    .catch(() => false);
  memoria.set(ruta, promesa);
  return promesa;
};

export const useExiste = (ruta: string | undefined): boolean | null => {
  const [existe, setExiste] = useState<boolean | null>(null);
  const [espera] = useState(() => delayRender(`Buscando ${ruta ?? "archivo"}`));
  useEffect(() => {
    let vivo = true;
    if (!ruta) {
      setExiste(false);
      continueRender(espera);
      return;
    }
    consultar(ruta).then((r) => {
      if (vivo) setExiste(r);
      continueRender(espera);
    });
    return () => {
      vivo = false;
    };
  }, [ruta, espera]);
  return existe;
};
