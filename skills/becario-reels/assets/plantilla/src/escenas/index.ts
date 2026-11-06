// Biblioteca de escenas: el "tipo" del plan → componente. Ver references/escenas.md para usarlas.
import type { DefEscena } from "../tipos";
import { chat, editor, movil } from "./apps";
import { cta } from "./cta";
import { galeria, imagen } from "./fotos";
import { barras, cifras, comparacion, contador, ficha, lista, objecion, pasos, pregunta, tachado } from "./tarjetas";
import { titular } from "./titular";

export const BIBLIOTECA: Record<string, DefEscena> = {
  titular,
  chat,
  tachado,
  contador,
  galeria,
  imagen,
  cifras,
  ficha,
  lista,
  comparacion,
  objecion,
  pasos,
  pregunta,
  barras,
  movil,
  editor,
  cta,
};
