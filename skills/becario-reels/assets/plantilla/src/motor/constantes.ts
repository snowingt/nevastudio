export const FPS = 30;
export const ANCHO = 1080;
export const ALTO = 1920;
/** Las palabras de los subtítulos aparecen unos fotogramas antes de oírse (así se leen a tiempo). */
export const ADELANTO = 4;
/** Fotogramas que se solapan dos escenas en un fundido suave. */
export const SOLAPE = 10;
/** Duración de la transición de semitono (el cambio de escena queda en el centro). */
export const SEMI = 18;
export const s2f = (s: number) => Math.round(s * FPS);
