// Línea de tiempo del reel: a partir del plan y de los tiempos de la voz calcula cuándo empieza y acaba
// cada escena, en qué fotograma entra cada elemento, los cambios de pose y los efectos de sonido.
// También junta todos los problemas del plan (palabras que no existen, escenas desconocidas…) para
// que `node render.mjs resumen` los enseñe de una vez antes de renderizar.
import tiempos0 from "../datos/tiempos.json";
import { BIBLIOTECA } from "../escenas";
import { PROPIAS } from "../propias";
import type { DefEscena, Entrada, Momento, PalabraEscena, Tiempos } from "../tipos";
import { C, CON_PERSONAJE, ESTILO, PLAN, POSE_BASE, POSES } from "./actual";
export { CON_PERSONAJE, ESTILO, PLAN, POSES };

import { ADELANTO, FPS, SOLAPE, s2f } from "./constantes";
export { ADELANTO, FPS, SOLAPE, s2f };

export const T = tiempos0 as unknown as Tiempos;

export const SONIDOS = ["pop", "ding", "exito", "campana", "tecla", "tic", "clic", "whoosh", "swoosh", "papel", "burbuja", "golpe", "negacion", "puff", "cristal", "proyector", "subida"];

export const PROBLEMAS: string[] = [];
const problema = (s: string) => PROBLEMAS.push(s);
/** Cosas mejorables que no impiden renderizar. */
export const AVISOS: string[] = [];
const aviso = (s: string) => AVISOS.push(s);

const N = Math.min(PLAN.frases.length, T.frases.length);
if (PLAN.frases.length !== T.frases.length)
  problema(`El plan tiene ${PLAN.frases.length} frases y tiempos.json tiene ${T.frases.length}. Vuelve a alinear la voz con el guion del plan (scripts/alinear.py).`);

export const TOTAL = Math.max(1, Math.ceil(T.duracion * FPS));

/** Hay voz si alinear.py la preparó (tiempos.json dice de qué audio salió) y el plan no la quita con "voz": false. */
export const HAY_VOZ = !!T.voz && PLAN.voz !== false;
if (T.voz && PLAN.voz === false) aviso(`El plan dice "voz": false pero hay una voz alineada (${T.voz}): el vídeo saldrá sin voz. Quita "voz": false si la quieres.`);

// colores que tienen que leerse uno encima de otro
const lum = (hex: string) => {
  const n = parseInt(hex.replace("#", "").slice(0, 6), 16);
  const c = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => {
    const x = v / 255;
    return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
};
const contraste = (a: string, b: string) => {
  const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p);
  return (x + 0.05) / (y + 0.05);
};
for (const [fondo, texto, nombre] of [
  ["acento", "acentoTexto", "el texto sobre el color de acento (cajas de subtítulos, botones)"],
  ["fondo", "texto", "el texto sobre el fondo"],
  ["tarjeta", "tarjetaTexto", "el texto de las tarjetas"],
  ["oscuro", "oscuroTexto", "el texto de los paneles oscuros"],
] as const) {
  const r = contraste(C[fondo], C[texto]);
  if (r < 3) aviso(`Estilo: ${nombre} contrasta poco (${r.toFixed(1)}:1, ${C[texto]} sobre ${C[fondo]}). Prueba ${lum(C[fondo]) > 0.3 ? "un texto oscuro" : "un texto claro"} en "${texto}".`);
}

// portada: la línea más larga decide el tamaño del título
if (PLAN.portada?.lineas?.length) {
  const larga = PLAN.portada.lineas.map((l) => l.replace(/\*/g, "")).reduce((a, l) => (l.length > a.length ? l : a), "");
  if (larga.length > 12) aviso(`Portada: la línea «${larga}» tiene ${larga.length} letras y el título sale pequeño en la miniatura. Usa líneas de 12 letras o menos (mejor 10).`);
}

const norm = (w: string) =>
  w
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9ñ]/g, "");

// si se cambia el texto de una frase después de alinear, los tiempos ya no valen
const soloTexto = (t: string) => norm(t.replace(/\[[^\]]*\]/g, " ").replace(/\*/g, ""));
const cambiadas = PLAN.frases.slice(0, N).map((fr, i) => (soloTexto(fr.texto ?? "") !== soloTexto(T.frases[i].texto ?? "") ? i + 1 : 0)).filter((k) => k > 0);
if (cambiadas.length)
  problema(`El texto de ${cambiadas.length === 1 ? "la frase" : "las frases"} ${cambiadas.join(", ")} ha cambiado desde que se alineó la voz. Vuelve a ejecutar alinear.py (con el audio, o con --sin-voz).`);

// ---------------------------------------------------------------- palabras y cortes

/** Corte de escena: 1 fotograma antes de que se oiga la primera palabra de la frase. */
export const corte = (i: number) => (i === 0 ? 0 : Math.max(0, s2f(T.frases[i].inicio) - 1));
export const finFrase = (i: number) => s2f(T.frases[i].fin);
const aparicion = (i: number, k: number) => Math.max(corte(i), s2f(T.frases[i].palabras[k].t) - ADELANTO);

export const entrada = (i: number): Entrada => {
  if (i === 0) return "corte";
  const e = PLAN.frases[i]?.entrada ?? PLAN.transicion ?? (ESTILO.familia === "suave" ? "suave" : "corte");
  return e;
};
/** Primer fotograma de la escena i. */
export const ini = (i: number) => (i === 0 ? 0 : entrada(i) === "suave" ? corte(i) - SOLAPE / 2 : corte(i));
/** Fotograma en que la escena i deja de verse. */
export const fin = (i: number) => (i + 1 < N ? (entrada(i + 1) === "suave" ? corte(i + 1) + SOLAPE / 2 : corte(i + 1)) : TOTAL);

/** Fotograma absoluto de un momento de la frase i (o null si no existe). */
export const momento = (i: number, m: Momento, quien = ""): number | null => {
  if (typeof m === "number") return ini(i) + m;
  const r = /^(.+?)(?:#(\d+))?([+-]\d+)?$/.exec(m.trim());
  if (!r) {
    problema(`Frase ${i + 1}${quien}: no entiendo el momento «${m}»`);
    return null;
  }
  const [, base, nTxt, offTxt] = r;
  const off = offTxt ? parseInt(offTxt, 10) : 0;
  if (base === "inicio") return corte(i) + off;
  if (base === "fin") return fin(i) - 1 + off;
  const objetivo = norm(base);
  const n = nTxt ? parseInt(nTxt, 10) : 1;
  const pal = T.frases[i].palabras;
  // primero la palabra exacta ("escribe" no es "Escribes"); si no está, la que empiece así ("anim" → "animación")
  const exactas = pal.map((p, k) => (norm(p.w) === objetivo ? k : -1)).filter((k) => k >= 0);
  const empiezan = pal.map((p, k) => (objetivo && norm(p.w).startsWith(objetivo) ? k : -1)).filter((k) => k >= 0);
  const lista = exactas.length >= n ? exactas : empiezan;
  if (lista.length >= n) return aparicion(i, lista[n - 1]) + off;
  problema(`Frase ${i + 1}${quien}: no encuentro «${base}»${n > 1 ? ` (vez ${n})` : ""}. Palabras: ${pal.map((p) => p.w).join(" ")}`);
  return null;
};

// ---------------------------------------------------------------- escenas

export const definicion = (i: number): DefEscena | null => {
  const e = PLAN.frases[i].escena;
  if (!e || !e.tipo) {
    problema(`Frase ${i + 1}: falta la escena`);
    return null;
  }
  if (e.tipo === "propia") {
    const d = PROPIAS[String(e.nombre)];
    if (!d) problema(`Frase ${i + 1}: no existe la escena propia «${e.nombre}». Propias: ${Object.keys(PROPIAS).join(", ") || "(ninguna)"}`);
    return d ?? null;
  }
  const d = BIBLIOTECA[e.tipo];
  if (!d) problema(`Frase ${i + 1}: no existe el tipo de escena «${e.tipo}». Tipos: ${Object.keys(BIBLIOTECA).join(", ")}`);
  return d ?? null;
};

export type EscenaLinea = {
  i: number;
  ini: number;
  fin: number;
  dur: number;
  entrada: Entrada;
  salida: Entrada | null;
  def: DefEscena | null;
  p: Record<string, unknown>;
  b: number[];
  palabras: PalabraEscena[];
};

/** Completa los momentos que falten repartiéndolos por la escena. */
const repartir = (dados: number[], n: number, dur: number) => {
  const b = [...dados];
  if (b.length >= n) return b;
  if (b.length === 0) {
    const hasta = Math.max(8, dur * 0.7);
    for (let k = 0; k < n; k++) b.push(Math.round(2 + (hasta - 2) * (n === 1 ? 0 : k / (n - 1))));
    return b;
  }
  const desde = b[b.length - 1];
  const hasta = Math.max(desde + 6, dur - 12);
  const faltan = n - b.length;
  for (let k = 1; k <= faltan; k++) b.push(Math.round(desde + ((hasta - desde) * k) / (faltan + 1)));
  return b;
};

export const ESCENAS: EscenaLinea[] = Array.from({ length: N }).map((_, i) => {
  const def = definicion(i);
  const e = PLAN.frases[i].escena ?? { tipo: "?" };
  const { en, ...resto } = e;
  const p: Record<string, unknown> = { ...resto };
  delete p.tipo;
  delete p.nombre;
  const a = ini(i);
  const dur = fin(i) - a;
  const dados = (en ?? []).map((m) => momento(i, m, ` (escena ${e.tipo})`)).filter((x): x is number => x !== null).map((x) => x - a);
  const n = def ? (typeof def.momentos === "function" ? def.momentos(p) : def.momentos) : 0;
  if (dados.length > n && n > 0) aviso(`Frase ${i + 1} (${e.tipo}): "en" tiene ${dados.length} momentos pero esta escena usa ${n}; los de más no hacen nada.`);
  const b = repartir(dados.slice(0, n), n, dur);
  if (def?.validar) def.validar(p).forEach((s) => problema(`Frase ${i + 1} (${e.tipo}): ${s}`));
  if (def?.avisar) def.avisar(p).forEach((s) => aviso(`Frase ${i + 1} (${e.tipo}): ${s}`));
  // lo último que entra tiene que verse un rato antes de que cambie la escena
  const ultimo = b.length ? b[b.length - 1] : 0;
  if (def && i + 1 < N && b.length && dur - ultimo < 15)
    aviso(`Frase ${i + 1} (${e.tipo}): el último elemento entra ${((dur - ultimo) / FPS).toFixed(1)} s antes de que cambie la escena y apenas se ve. Ponlo en una palabra anterior.`);
  if (e.tipo === "pregunta" && b.length >= 3 && b[2] - b[1] < 30)
    aviso(`Frase ${i + 1} (pregunta): las opciones salen ${((b[2] - b[1]) / FPS).toFixed(1)} s antes de la solución; deja al menos 1 s para leerlas (adelanta el segundo momento).`);
  // pantalla vacía al principio: lo primero entra demasiado tarde (titular, chat y editor ya se ven desde el inicio)
  const vacio = b.length ? b[0] + a - corte(i) : 0;
  if (def && !["titular", "chat", "editor"].includes(e.tipo) && !def.alInicio?.(p) && vacio > 24)
    aviso(`Frase ${i + 1} (${e.tipo}): durante ${(vacio / FPS).toFixed(1)} s no se ve nada de la escena (solo los subtítulos). Pon el primer momento de "en" en una palabra anterior (o "inicio").`);
  const palabras = T.frases[i].palabras.map((w, k) => ({ w: w.w, f: aparicion(i, k) - a, clave: !!w.clave, g: w.g ?? -1 }));
  return { i, ini: a, fin: fin(i), dur, entrada: entrada(i), salida: i + 1 < N ? entrada(i + 1) : null, def, p, b, palabras };
});

// ---------------------------------------------------------------- poses y sonidos

export const CAMBIOS_POSE: { desde: number; pose: string }[] = [];
if (CON_PERSONAJE) {
  PLAN.frases.slice(0, N).forEach((fr, i) =>
    (fr.poses ?? []).forEach(([m, pose]) => {
      const t = momento(i, m, " (poses)");
      if (!POSES[pose]) problema(`Frase ${i + 1}: no existe la pose «${pose}». Poses: ${Object.keys(POSES).join(", ")}`);
      else if (t !== null) CAMBIOS_POSE.push({ desde: t, pose });
    }),
  );
  CAMBIOS_POSE.sort((x, y) => x.desde - y.desde);
  if (CAMBIOS_POSE.length === 0 && Object.keys(POSES).length) CAMBIOS_POSE.push({ desde: 0, pose: POSE_BASE });
  else if (CAMBIOS_POSE.length && CAMBIOS_POSE[0].desde > 0) CAMBIOS_POSE.unshift({ desde: 0, pose: CAMBIOS_POSE[0].pose });
}

export type Efecto = { en: number; s: string; vol: number };
export const EFECTOS: Efecto[] = [];
ESCENAS.forEach((esc) => {
  if (esc.def?.sonidos)
    esc.def.sonidos(esc.p, esc.b).forEach(([k, s, vol]) => {
      const t = esc.b[k];
      if (t !== undefined) EFECTOS.push({ en: esc.ini + t, s, vol });
    });
  (PLAN.frases[esc.i].sonidos ?? []).forEach(([m, s, vol]) => {
    const t = momento(esc.i, m, " (sonidos)");
    if (!SONIDOS.includes(s)) problema(`Frase ${esc.i + 1}: el sonido «${s}» no está en public/sonidos (${SONIDOS.join(", ")})`);
    else if (t !== null) EFECTOS.push({ en: t, s, vol: vol ?? 0.3 });
  });
});
EFECTOS.sort((x, y) => x.en - y.en);

/** Resumen para `node render.mjs resumen`. */
export const resumen = () => ({
  duracion: +(TOTAL / FPS).toFixed(2),
  estilo: ESTILO.nombre,
  escenas: ESCENAS.map((e) => ({
    frase: e.i + 1,
    tipo: PLAN.frases[e.i].escena?.tipo === "propia" ? `propia:${PLAN.frases[e.i].escena.nombre}` : PLAN.frases[e.i].escena?.tipo,
    desde: +(e.ini / FPS).toFixed(2),
    hasta: +(e.fin / FPS).toFixed(2),
    entrada: e.entrada,
    momentos: e.b.map((x) => +((e.ini + x) / FPS).toFixed(2)),
  })),
  efectos: EFECTOS.length,
  poses: CAMBIOS_POSE.length,
  problemas: PROBLEMAS,
  avisos: AVISOS,
  /** Lo que necesita render.mjs para mezclar el audio con ffmpeg (más rápido que renderizarlo). */
  audio: { fotogramas: TOTAL, voz: HAY_VOZ ? "voz.wav" : null, efectos: EFECTOS.map((e) => ({ en: e.en, s: e.s, vol: e.vol })) },
});
