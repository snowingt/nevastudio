// Carga las fuentes del estilo desde public/fuentes con los nombres genéricos (BRTitulo, BRTexto, BRMano, BRMono).
// El render espera a que estén cargadas, y las piezas que miden texto usan useFuentes().
import { useEffect, useState } from "react";
import { continueRender, delayRender, staticFile } from "remotion";
import { ESTILO } from "./actual";
import { F, type Fuente } from "./estilos";

const caras: [string, Fuente][] = [
  [F.titulo, ESTILO.fuentes.titulo],
  ...ESTILO.fuentes.texto.map((f) => [F.texto, f] as [string, Fuente]),
  [F.mano, ESTILO.fuentes.mano],
  ...ESTILO.fuentes.mono.map((f) => [F.mono, f] as [string, Fuente]),
];

const handle = delayRender("Cargando fuentes");

export const fuentesListas: Promise<void> = Promise.all(
  caras.map(([familia, fu]) => {
    const f = new FontFace(familia, `url(${staticFile(fu.archivo)})`, { weight: String(fu.peso) });
    (document.fonts as unknown as { add: (cara: FontFace) => void }).add(f);
    return f.load().catch((e) => {
      throw new Error(`No se pudo cargar la fuente ${fu.archivo}: ${e}`);
    });
  }),
).then(() => {
  continueRender(handle);
});

let listas = false;
fuentesListas.then(() => {
  listas = true;
});

/** true cuando las fuentes ya se pueden medir. */
export const useFuentes = () => {
  const [ok, setOk] = useState(listas);
  useEffect(() => {
    if (!ok) fuentesListas.then(() => setOk(true));
  }, [ok]);
  return ok;
};

/** Peso más cercano disponible para el texto (para no pedir 700 si solo hay 600 y 800). */
export const pesoTexto = (quiero: number) =>
  ESTILO.fuentes.texto.map((f) => f.peso).reduce((a, b) => (Math.abs(b - quiero) < Math.abs(a - quiero) ? b : a));
