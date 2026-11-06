// Lo que todas las piezas necesitan saber del reel actual: estilo, colores y dónde va cada cosa en pantalla.
// (Separado de linea.ts para que las escenas lo puedan importar sin crear un ciclo.)
import plan0 from "../datos/plan.json";
import poses0 from "../datos/poses.json";
import type { Plan } from "../tipos";
import { resolverEstilo } from "./estilos";

export const PLAN = plan0 as unknown as Plan;
export const ESTILO = resolverEstilo(PLAN.estilo);
/** Colores del estilo con nombre de uso. */
export const C = ESTILO.colores;
export const SUAVE = ESTILO.familia === "suave";

export type MedidasPose = { src: string; ancho: number; alto: number; cabeza: number; anchoCabeza: number; peloArriba: number };
/** Poses del personaje medidas por scripts/poses.py (las claves que empiezan por "_" son datos internos). */
export const POSES: Record<string, MedidasPose> = {};
for (const [k, v] of Object.entries(poses0 as Record<string, unknown>)) if (!k.startsWith("_")) POSES[k] = v as MedidasPose;
export const CON_PERSONAJE = (PLAN.personaje ?? true) && Object.keys(POSES).length > 0;
/** Pose por defecto: la de referencia de poses.py ("normal" si existe) o la primera. */
const ref = (poses0 as Record<string, unknown>)["_referencia"];
export const POSE_BASE = typeof ref === "string" && POSES[ref] ? ref : POSES.normal ? "normal" : Object.keys(POSES)[0];
export const SUBTITULOS = PLAN.subtitulos ?? "linea";

/** Zona de diseño de las escenas: se dibujan con coordenadas de pantalla dentro de este rectángulo. */
export const LIENZO = { x: 60, y: 210, w: 960, h: 860 };

/** Dónde cabe la escena según los subtítulos y el personaje (el lienzo se escala y centra aquí). */
export const ZONA =
  SUBTITULOS === "bloque"
    ? CON_PERSONAJE
      ? { x: 60, y: 500, w: 960, h: 740 }
      : { x: 60, y: 500, w: 960, h: 1000 }
    : CON_PERSONAJE
      ? { x: 60, y: 210, w: 960, h: 860 }
      : { x: 60, y: 250, w: 960, h: 960 };

/** Centro vertical de la línea de subtítulos (modo "linea"). */
export const SUB_Y = CON_PERSONAJE ? 1170 : 1330;

/** Sombra de las tarjetas según la familia del estilo. */
export const SOMBRA = SUAVE ? "0 26px 54px rgba(40, 30, 60, 0.18), 0 8px 16px rgba(40, 30, 60, 0.10)" : `10px 12px 0 ${C.borde}`;
export const SOMBRA_PEQ = SUAVE ? "0 10px 22px rgba(40, 30, 60, 0.16), 0 3px 6px rgba(40, 30, 60, 0.10)" : `5px 6px 0 ${C.borde}`;
/** Borde de las tarjetas (solo en la familia "marcado"). */
export const BORDE = SUAVE ? "none" : `5px solid ${C.borde}`;
