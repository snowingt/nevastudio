// Escenas propias: cuando ninguna escena de la biblioteca encaja con una frase, se escribe una aquí
// (copia Ejemplo.tsx), se registra en esta lista y se usa en el plan con
//   "escena": { "tipo": "propia", "nombre": "MiEscena", "en": ["palabra", …], …props }
import type { DefEscena } from "../tipos";
import { ejemplo } from "./Ejemplo";

export const PROPIAS: Record<string, DefEscena> = {
  Ejemplo: ejemplo,
};
