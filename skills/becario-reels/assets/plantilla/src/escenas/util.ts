// Ayudas para leer y comprobar las propiedades de las escenas que vienen del plan (JSON).
import { existeIcono } from "../piezas/basicas";

export const txt = (p: Record<string, unknown>, k: string, def = ""): string => (typeof p[k] === "string" ? (p[k] as string) : typeof p[k] === "number" ? String(p[k]) : def);
export const num = (p: Record<string, unknown>, k: string, def = 0): number => (typeof p[k] === "number" ? (p[k] as number) : typeof p[k] === "string" && !isNaN(Number(p[k])) ? Number(p[k]) : def);
export const bool = (p: Record<string, unknown>, k: string, def = false): boolean => (typeof p[k] === "boolean" ? (p[k] as boolean) : def);
export const arr = <T = unknown>(p: Record<string, unknown>, k: string): T[] => (Array.isArray(p[k]) ? (p[k] as T[]) : []);
export const obj = (p: Record<string, unknown>, k: string): Record<string, unknown> => (p[k] && typeof p[k] === "object" && !Array.isArray(p[k]) ? (p[k] as Record<string, unknown>) : {});

/** Elemento de lista que puede venir como texto o como {texto, icono}. */
export const item = (x: unknown): { texto: string; icono?: string } =>
  typeof x === "string" ? { texto: x } : x && typeof x === "object" ? { texto: String((x as Record<string, unknown>).texto ?? ""), icono: (x as Record<string, unknown>).icono as string | undefined } : { texto: String(x ?? "") };

// ---------------------------------------------------------------- validación

type Regla = [campo: string, tipo: "texto" | "numero" | "lista" | "objeto" | "imagen", opciones?: { max?: number; min?: number; opcional?: boolean; maxItems?: number; minItems?: number }];

/** Comprueba campos obligatorios, tipos y longitudes. Devuelve frases legibles para el usuario. */
export const reglas = (p: Record<string, unknown>, lista: Regla[]): string[] => {
  const out: string[] = [];
  for (const [campo, tipo, o = {}] of lista) {
    const v = p[campo];
    if (v === undefined || v === null || v === "") {
      if (!o.opcional) out.push(`falta «${campo}»`);
      continue;
    }
    if ((tipo === "texto" || tipo === "imagen") && typeof v !== "string") out.push(`«${campo}» tiene que ser un texto`);
    if (tipo === "numero" && typeof v !== "number") out.push(`«${campo}» tiene que ser un número`);
    if (tipo === "lista" && !Array.isArray(v)) out.push(`«${campo}» tiene que ser una lista`);
    if (tipo === "objeto" && (typeof v !== "object" || Array.isArray(v))) out.push(`«${campo}» tiene que ser un objeto {…}`);
    if (typeof v === "string" && o.max && v.replace(/\*/g, "").length > o.max) out.push(`«${campo}» es demasiado largo (${v.length} letras; máximo ${o.max}). Acórtalo para que se lea en pantalla`);
    if (Array.isArray(v) && o.maxItems && v.length > o.maxItems) out.push(`«${campo}» tiene ${v.length} elementos; como mucho ${o.maxItems}`);
    if (Array.isArray(v) && o.minItems && v.length < o.minItems) out.push(`«${campo}» necesita al menos ${o.minItems} elementos`);
    if (tipo === "imagen" && typeof v === "string" && !/\.(png|jpe?g|webp)$/i.test(v)) out.push(`«${campo}» tiene que ser una imagen .png, .jpg o .webp de public/ (por ejemplo "imagenes/foto.png")`);
  }
  return out;
};

export const iconos = (nombres: (string | undefined)[]): string[] =>
  nombres.filter((n): n is string => !!n && !existeIcono(n)).map((n) => `el icono «${n}» no existe (busca nombres en https://lucide.dev/icons, por ejemplo "rocket" o "shopping-cart")`);

/** Normaliza para comparar palabras (sin tildes ni signos). */
export const norm = (w: string) =>
  w
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9ñ]/g, "");
