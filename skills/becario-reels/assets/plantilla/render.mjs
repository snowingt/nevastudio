// Renderiza el reel con la API de Node de Remotion (sin la CLI).
//
//   node render.mjs resumen                 comprueba el plan y enseña escenas, momentos y problemas (no renderiza)
//   node render.mjs fotos [cada]            hoja de contacto en salida/hoja.png (por escena: la mitad, cada momento y el final;
//                                           con "cada" en segundos, uno cada tantos segundos)
//   node render.mjs video [--borrador]      vídeo final en salida/reel.mp4, por trozos (se puede relanzar y sigue donde iba)
//   node render.mjs foto 12.5 [20 …]        fotogramas sueltos a tamaño completo en salida/foto_12.50.png
//   node render.mjs portada                 portada en salida/portada.png y su comprobación en salida/portada_check.png
//
// Opciones: --max-segundos 270 (para antes de que corte el tiempo de un comando; vuelve a lanzarlo y sigue),
//           --forzar (renderiza aunque el resumen tenga problemas), --crf 20 (calidad: menos = mejor y más pesado),
//           --hilos 2 (pestañas del navegador renderizando a la vez; bájalo si se queda sin memoria),
//           --limite-mb 28 (si el vídeo pesa más, se recomprime para que se pueda descargar).
import { bundle } from "@remotion/bundler";
import { openBrowser, renderMedia, renderStill, selectComposition } from "@remotion/renderer";
import crypto from "node:crypto";
import { execFileSync, spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Remotion avisa de la memoria del contenedor en cada render: es ruido, se quita de la salida.
const RUIDO = /Memory reported by|inadvertently set the --memory|Using the lower amount of memory|Detected differing memory amounts/;
for (const s of [process.stdout, process.stderr]) {
  const escribir = s.write.bind(s);
  s.write = (trozo, ...resto) => {
    const texto = typeof trozo === "string" ? trozo : Buffer.from(trozo).toString("utf8");
    if (!RUIDO.test(texto)) return escribir(trozo, ...resto);
    const limpio = texto.split("\n").filter((l) => !RUIDO.test(l)).join("\n");
    return limpio.trim() ? escribir(limpio, ...resto) : true;
  };
}

const RAIZ = path.dirname(fileURLToPath(import.meta.url));
const SALIDA = path.join(RAIZ, "salida");
const TROZOS = path.join(SALIDA, "trozos");
const args = process.argv.slice(2);
const cmd = args[0] ?? "resumen";
const opt = (n, def) => {
  const i = args.indexOf(`--${n}`);
  return i >= 0 ? args[i + 1] : def;
};
const flag = (n) => args.includes(`--${n}`);
const t0 = Date.now();
const seg = () => ((Date.now() - t0) / 1000).toFixed(1);
const MAX_SEG = Number(opt("max-segundos", 270));
// 30 MB es el límite de descarga de archivos en la app de Claude; dejamos margen.
const LIMITE_MB = Number(opt("limite-mb", 28));
fs.mkdirSync(SALIDA, { recursive: true });

// ------------------------------------------------------------ navegador y ffmpeg (los encuentra preparar.py)
const entorno = fs.existsSync(path.join(RAIZ, "entorno.json")) ? JSON.parse(fs.readFileSync(path.join(RAIZ, "entorno.json"), "utf8")) : {};
let navegador = process.env.BROWSER_EXECUTABLE || entorno.navegador || null;
// el Chromium que viene en npm (@sparticuz/chromium) se descomprime en /tmp: si ya no está, se vuelve a sacar
if (navegador && !fs.existsSync(navegador) && fs.existsSync(path.join(RAIZ, "node_modules", "@sparticuz", "chromium"))) {
  const m = await import("@sparticuz/chromium");
  navegador = await (m.default ?? m).executablePath();
}
const modoChrome = entorno.modo || (navegador && /headless[-_]shell/.test(navegador) ? "headless-shell" : navegador ? "chrome-for-testing" : "headless-shell");
const opcNav = { browserExecutable: navegador, chromeMode: modoChrome };

const ffmpeg = () => {
  if (entorno.ffmpeg && fs.existsSync(entorno.ffmpeg)) return { bin: entorno.ffmpeg, env: process.env };
  const sistema = spawnSync("ffmpeg", ["-version"], { stdio: "ignore" });
  if (sistema.status === 0) return { bin: "ffmpeg", env: process.env };
  // el ffmpeg que trae Remotion (con sus librerías al lado)
  const dir = path.join(RAIZ, "node_modules", "@remotion", `compositor-${process.platform}-${process.arch === "x64" ? "x64" : "arm64"}${process.platform === "linux" ? "-gnu" : ""}`);
  const bin = path.join(dir, process.platform === "win32" ? "ffmpeg.exe" : "ffmpeg");
  if (fs.existsSync(bin)) return { bin, env: { ...process.env, LD_LIBRARY_PATH: `${dir}:${process.env.LD_LIBRARY_PATH ?? ""}`, DYLD_LIBRARY_PATH: dir } };
  throw new Error("No encuentro ffmpeg. Ejecuta python3 scripts/preparar.py otra vez o instala imageio-ffmpeg (pip install imageio-ffmpeg).");
};
const ff = (argumentos) => {
  const { bin, env } = ffmpeg();
  return execFileSync(bin, ["-hide_banner", "-loglevel", "error", "-y", ...argumentos], { env, stdio: ["ignore", "pipe", "pipe"] });
};

// ------------------------------------------------------------ audio: voz + efectos mezclados con ffmpeg
// (igual que en la composición: la voz desde el principio y cada efecto en su fotograma, como mucho 2 s)
const mezclarAudio = (a, fps, destino) => {
  const dur = (a.fotogramas / fps).toFixed(3);
  const entradas = [];
  const filtros = [];
  const pistas = [];
  const voz = a.voz ? path.join(RAIZ, "public", a.voz) : null;
  if (voz && fs.existsSync(voz)) entradas.push("-i", voz);
  else {
    if (voz) console.log(`AVISO: no encuentro public/${a.voz}; el vídeo saldrá sin voz.`);
    entradas.push("-f", "lavfi", "-t", dur, "-i", "anullsrc=r=48000:cl=stereo");
  }
  filtros.push(`[0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad=whole_dur=${dur}[a0]`);
  pistas.push("[a0]");
  a.efectos.forEach((e, k) => {
    const archivo = path.join(RAIZ, "public", "sonidos", `${e.s}.wav`);
    if (!fs.existsSync(archivo)) return;
    entradas.push("-i", archivo);
    const n = entradas.filter((x) => x === "-i").length - 1;
    const ms = Math.max(0, Math.round((e.en / fps) * 1000));
    filtros.push(`[${n}:a]atrim=0:2,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume=${e.vol},adelay=${ms}|${ms}[e${k}]`);
    pistas.push(`[e${k}]`);
  });
  filtros.push(`${pistas.join("")}amix=inputs=${pistas.length}:normalize=0:duration=first,atrim=0:${dur}[m]`);
  ff([...entradas, "-filter_complex", filtros.join(";"), "-map", "[m]", "-c:a", "pcm_s16le", "-ar", "48000", destino]);
};

// ------------------------------------------------------------ empaquetado (se reutiliza si no ha cambiado nada)
// soloVideo: para los trozos del vídeo no cuenta la portada (cambiarla no obliga a renderizar el vídeo otra vez)
const huella = (soloVideo = false) => {
  const h = crypto.createHash("sha1");
  const plan = path.join(RAIZ, "src", "datos", "plan.json");
  const recorrer = (d) => {
    for (const e of fs.readdirSync(d, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      const p = path.join(d, e.name);
      if (e.isDirectory()) recorrer(p);
      else if (soloVideo && p === plan) {
        try {
          const j = JSON.parse(fs.readFileSync(p, "utf8"));
          delete j.portada;
          h.update(`${p}:${JSON.stringify(j)}`);
        } catch {
          h.update(fs.readFileSync(p));
        }
      } else {
        const st = fs.statSync(p);
        h.update(`${p}:${st.size}:${st.mtimeMs}`);
      }
    }
  };
  recorrer(path.join(RAIZ, "src"));
  recorrer(path.join(RAIZ, "public"));
  return h.digest("hex").slice(0, 12);
};

const empaquetar = async () => {
  const id = huella();
  const destino = path.join(os.tmpdir(), `becario-reels-${id}`);
  if (fs.existsSync(path.join(destino, "index.html"))) return destino;
  const url = await bundle({ entryPoint: path.join(RAIZ, "src", "index.ts"), publicDir: path.join(RAIZ, "public"), outDir: destino, onProgress: () => {} });
  console.log(`empaquetado en ${seg()} s`);
  return url;
};

const abrirNavegador = () => openBrowser("chrome", { browserExecutable: navegador, chromeMode: modoChrome, logLevel: "error" });

const elegir = async (serveUrl, id, browser, inputProps = {}) => selectComposition({ serveUrl, id, inputProps, puppeteerInstance: browser, ...opcNav, logLevel: "error" });

// ------------------------------------------------------------ resumen
const enseñarResumen = (r) => {
  console.log(`\nDuración ${r.duracion} s · estilo ${r.estilo} · ${r.escenas.length} escenas · ${r.efectos} efectos de sonido · ${r.poses} cambios de pose\n`);
  for (const e of r.escenas) console.log(`  ${String(e.frase).padStart(2)}. ${String(e.tipo).padEnd(12)} ${e.desde.toFixed(2)}–${e.hasta.toFixed(2)} s  (${e.entrada})  momentos: ${e.momentos.join(", ")}`);
  if (r.problemas.length) {
    console.log(`\nPROBLEMAS (${r.problemas.length}):`);
    for (const p of r.problemas) console.log(`  - ${p}`);
  } else console.log("\nSin problemas en el plan.");
  if (r.avisos?.length) {
    console.log(`\nAVISOS (${r.avisos.length}; no impiden renderizar, pero se notan en el vídeo):`);
    for (const a of r.avisos) console.log(`  - ${a}`);
  }
};

// ------------------------------------------------------------ comandos
const main = async () => {
  const serveUrl = await empaquetar();
  const browser = await abrirNavegador();
  try {
    if (cmd === "resumen") {
      const comp = await elegir(serveUrl, "Reel", browser);
      enseñarResumen(comp.props.resumen);
      process.exitCode = comp.props.resumen.problemas.length ? 1 : 0;
      return;
    }

    if (cmd === "fotos") {
      const comp = await elegir(serveUrl, "Reel", browser);
      const r = comp.props.resumen;
      const cada = args[1] && !args[1].startsWith("--") ? Number(args[1]) : 0;
      let marcas = [];
      if (cada > 0) for (let t = 0.3; t < r.duracion; t += cada) marcas.push(t);
      // por escena: la mitad, cada momento y cómo queda justo antes de cambiar (así se ve el titular entero)
      else for (const e of r.escenas) marcas.push((e.desde + e.hasta) / 2, ...e.momentos.map((m) => m + 0.25), e.hasta - 0.3);
      marcas = [...new Set(marcas.map((t) => Math.min(comp.durationInFrames - 1, Math.max(0, Math.round(t * comp.fps)))))].sort((a, b) => a - b);
      const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "hoja-"));
      const teselas = [];
      const escenaDe = (t) => r.escenas.filter((e) => t >= e.desde - 1e-6).pop();
      for (const f of marcas) {
        const out = path.join(tmp, `f${f}.jpeg`);
        await renderStill({ serveUrl, composition: comp, frame: f, output: out, imageFormat: "jpeg", jpegQuality: 80, scale: 300 / 1080, puppeteerInstance: browser, ...opcNav, logLevel: "error" });
        const e = escenaDe(f / comp.fps);
        teselas.push({ src: `data:image/jpeg;base64,${fs.readFileSync(out).toString("base64")}`, etiqueta: `${(f / comp.fps).toFixed(2)} s · ${e ? `${e.frase}. ${e.tipo}` : ""}` });
      }
      const mosaico = await elegir(serveUrl, "Mosaico", browser, { teselas });
      await renderStill({ serveUrl, composition: mosaico, output: path.join(SALIDA, "hoja.png"), inputProps: { teselas }, puppeteerInstance: browser, ...opcNav, logLevel: "error" });
      fs.rmSync(tmp, { recursive: true, force: true });
      console.log(`hoja de contacto con ${marcas.length} fotogramas en salida/hoja.png (${seg()} s). Ábrela y mírala entera.`);
      return;
    }

    if (cmd === "foto") {
      // fotogramas sueltos a tamaño completo, para mirar un momento de cerca
      const comp = await elegir(serveUrl, "Reel", browser);
      const tiempos = args.slice(1).filter((a) => !a.startsWith("--")).map(Number).filter((n) => Number.isFinite(n));
      if (!tiempos.length) throw new Error("Dime en qué segundo: node render.mjs foto 12.5 [20 …]");
      for (const t of tiempos) {
        const f = Math.min(comp.durationInFrames - 1, Math.max(0, Math.round(t * comp.fps)));
        const out = path.join(SALIDA, `foto_${(f / comp.fps).toFixed(2)}.png`);
        await renderStill({ serveUrl, composition: comp, frame: f, output: out, puppeteerInstance: browser, ...opcNav, logLevel: "error" });
        console.log(`salida/${path.basename(out)}`);
      }
      return;
    }

    if (cmd === "portada") {
      const comp = await elegir(serveUrl, "Portada", browser);
      await renderStill({ serveUrl, composition: comp, output: path.join(SALIDA, "portada.png"), puppeteerInstance: browser, ...opcNav });
      const chk = await elegir(serveUrl, "PortadaCheck", browser);
      await renderStill({ serveUrl, composition: chk, output: path.join(SALIDA, "portada_check.png"), puppeteerInstance: browser, ...opcNav });
      console.log(`portada en salida/portada.png y comprobación del recorte 3:4 en salida/portada_check.png (${seg()} s)`);
      return;
    }

    if (cmd === "video") {
      const comp = await elegir(serveUrl, "Reel", browser);
      const r = comp.props.resumen;
      if (r.problemas.length && !flag("forzar")) {
        enseñarResumen(r);
        console.log("\nArregla los problemas (o usa --forzar) antes de renderizar.");
        process.exitCode = 1;
        return;
      }
      const borrador = flag("borrador");
      const escala = borrador ? 0.5 : 1;
      const crf = Number(opt("crf", borrador ? 26 : 20));
      const TROZO = 240; // 8 s por trozo: cada trozo tarda poco y se puede seguir si se corta
      const total = comp.durationInFrames;
      const clave = `${huella(true)}-${escala}-${crf}`;
      const dirT = path.join(TROZOS, clave);
      fs.mkdirSync(dirT, { recursive: true });
      const n = Math.ceil(total / TROZO);
      const conc = Math.max(1, Number(opt("hilos", Math.min(os.cpus().length, 4))));
      for (let k = 0; k < n; k++) {
        const archivo = path.join(dirT, `${String(k).padStart(3, "0")}.mp4`);
        if (fs.existsSync(archivo) && fs.statSync(archivo).size > 1000) continue;
        if ((Date.now() - t0) / 1000 > MAX_SEG) {
          console.log(`PARCIAL: hechos ${k} de ${n} trozos. Vuelve a lanzar el mismo comando y seguirá desde aquí.`);
          process.exitCode = 3;
          return;
        }
        const a = k * TROZO,
          b = Math.min(total - 1, (k + 1) * TROZO - 1);
        await renderMedia({ serveUrl, composition: comp, codec: "h264", muted: true, frameRange: [a, b], outputLocation: archivo + ".tmp.mp4", crf, x264Preset: "veryfast", scale: escala, concurrency: conc, imageFormat: "jpeg", jpegQuality: 92, puppeteerInstance: browser, ...opcNav, logLevel: "error", pixelFormat: "yuv420p" });
        fs.renameSync(archivo + ".tmp.mp4", archivo);
        console.log(`trozo ${k + 1}/${n} (fotogramas ${a}–${b}) listo · ${seg()} s`);
      }
      const audio = path.join(dirT, "audio.wav");
      if (!fs.existsSync(audio)) mezclarAudio(r.audio, comp.fps, audio);
      const lista = path.join(dirT, "lista.txt");
      fs.writeFileSync(lista, Array.from({ length: n }, (_, k) => `file '${path.join(dirT, `${String(k).padStart(3, "0")}.mp4`)}'`).join("\n"));
      const final = path.join(SALIDA, borrador ? "borrador.mp4" : "reel.mp4");
      ff(["-f", "concat", "-safe", "0", "-i", lista, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", final]);
      let mb = fs.statSync(final).size / 1e6;
      if (mb > LIMITE_MB) {
        // la app de Claude no deja descargar archivos de más de 30 MB: se recomprime a la tasa justa
        const kbps = Math.floor(((LIMITE_MB * 8e6) / (total / comp.fps) - 200e3) / 1000);
        ff(["-i", final, "-c:v", "libx264", "-preset", "veryfast", "-b:v", `${kbps}k`, "-maxrate", `${Math.round(kbps * 1.3)}k`, "-bufsize", `${kbps * 2}k`, "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", final + ".tmp.mp4"]);
        fs.renameSync(final + ".tmp.mp4", final);
        mb = fs.statSync(final).size / 1e6;
      }
      console.log(`LISTO: ${path.relative(RAIZ, final)} · ${(total / comp.fps).toFixed(1)} s · ${mb.toFixed(1)} MB · ${seg()} s`);
      return;
    }
    console.log("Comandos: resumen | fotos [cada] | foto <segundos…> | video [--borrador] | portada");
  } finally {
    await browser.close({ silent: true });
  }
};

main().catch((e) => {
  console.error(`ERROR: ${e.message ?? e}`);
  process.exit(2);
});
