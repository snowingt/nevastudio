#!/usr/bin/env python3
"""Herramientas para los clips del usuario: ver, escuchar y cortar.

Uso:
  python3 scripts/trozos.py hoja CLIP.mp4 [--cada 2]            hoja de miniaturas con el segundo de cada una → CLIP_hoja.png
  python3 scripts/trozos.py transcribir CLIP.mp4 [--idioma es]  lo que se dice y cuándo → CLIP_transcripcion.txt
  python3 scripts/trozos.py cortar CLIP.mp4 DESDE HASTA NOMBRE [--carpeta P/clips] [--con-audio]
                                                                trozo corto, sin audio (por defecto) → P/clips/NOMBRE.mp4

- «hoja» sirve para elegir momentos sin mirar el vídeo fotograma a fotograma (una sola imagen).
- «transcribir» sirve para encontrar las frases que quieres citar y su segundo exacto.
- Los trozos salen a 640 px de ancho, 30 fps y sin el audio del clip. Apunta de dónde sale cada uno en CARPETA/lista.txt.
"""
import argparse, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import FFMPEG, fuente, duracion_media  # noqa: E402


def hoja(clip, cada, salida):
    dur = duracion_media(clip)
    if dur / cada > 48:
        cada = math.ceil(dur / 48)
        print(f"  El clip es largo: una miniatura cada {cada} s (48 como mucho). Usa --cada para cambiarlo.")
    tiempos = [t for t in np.arange(0, dur, cada)]
    tw = 240
    imgs = []
    for t in tiempos:
        raw = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{t:.2f}", "-i", clip, "-frames:v", "1", "-vf", f"scale={tw}:-2",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        if not raw:
            continue
        th = len(raw) // (tw * 3)
        imgs.append((t, Image.frombytes("RGB", (tw, th), raw[:tw * th * 3])))
    if not imgs:
        sys.exit(f"No he podido leer {clip}.")
    th = imgs[0][1].height
    cols = 6
    filas = math.ceil(len(imgs) / cols)
    out = Image.new("RGB", (cols * (tw + 6) + 6, filas * (th + 30) + 6), (30, 30, 30))
    d = ImageDraw.Draw(out)
    for k, (t, im) in enumerate(imgs):
        x, y = 6 + (k % cols) * (tw + 6), 6 + (k // cols) * (th + 30)
        out.paste(im, (x, y))
        d.text((x + 4, y + th + 3), f"{int(t // 60)}:{t % 60:04.1f}  ({t:.1f} s)", font=fuente("bold", 18), fill=(240, 240, 240))
    out.save(salida)
    print("Hoja:", salida)


def tiene_audio(clip):
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", clip], capture_output=True, text=True)
    return "Audio:" in r.stderr


def transcribir(clip, idioma, salida, modelo=None):
    import alinear as al
    if not tiene_audio(clip):
        sys.exit(f"{clip} no tiene sonido (es un vídeo sin pista de audio), así que no hay nada que transcribir. "
                 "Usa el clip original con audio.")
    a16 = al.leer_audio(clip, al.SR)
    segs = al.transcribir(a16, idioma, modelo)
    if segs is None:
        sys.exit("No he podido transcribir (falta faster-whisper o el modelo). Mira referencias/problemas.md.")
    with open(salida, "w", encoding="utf-8") as fh:
        for t0, t1, tx in segs:
            linea = f"{t0:7.2f}–{t1:7.2f}  {tx}"
            print(linea)
            fh.write(linea + "\n")
    print("Transcripción:", salida)
    print("Ojo: es automática. Para una cita, escucha el tramo y copia lo que dice de verdad.")


def cortar(clip, desde, hasta, nombre, carpeta, con_audio):
    os.makedirs(carpeta, exist_ok=True)
    if hasta <= desde:
        sys.exit("HASTA tiene que ser mayor que DESDE (en segundos).")
    if hasta - desde > 6:
        print("  Aviso: el trozo dura más de 6 s. Para comentar una obra de otros, usa trozos cortos.")
    salida = os.path.join(carpeta, nombre if nombre.endswith(".mp4") else nombre + ".mp4")
    cmd = [FFMPEG, "-v", "error", "-y", "-ss", f"{desde:.3f}", "-t", f"{hasta - desde:.3f}", "-i", clip,
           "-vf", "scale=640:-2,fps=30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p"]
    cmd += ["-c:a", "aac", "-b:a", "160k"] if con_audio else ["-an"]
    r = subprocess.run(cmd + [salida], capture_output=True, text=True)
    if r.returncode:
        sys.exit("ffmpeg falló: " + r.stderr[-400:])
    with open(os.path.join(carpeta, "lista.txt"), "a", encoding="utf-8") as fh:
        fh.write(f"{os.path.basename(salida)}\t{os.path.basename(clip)}\t{desde:.2f}\t{hasta:.2f}\n")
    clave = os.path.splitext(os.path.basename(salida))[0]
    print(f"Trozo: {salida} ({hasta - desde:.1f} s)")
    print(f'  En video.json, dentro de "clips": "{clave}": "{os.path.relpath(salida)}"')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="orden", required=True)
    h = sub.add_parser("hoja"); h.add_argument("clip"); h.add_argument("--cada", type=float, default=2.0); h.add_argument("--salida")
    t = sub.add_parser("transcribir"); t.add_argument("clip"); t.add_argument("--idioma", default="es"); t.add_argument("--salida")
    t.add_argument("--modelo")
    c = sub.add_parser("cortar"); c.add_argument("clip"); c.add_argument("desde", type=float); c.add_argument("hasta", type=float)
    c.add_argument("nombre"); c.add_argument("--carpeta", default="clips"); c.add_argument("--con-audio", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(a.clip):
        sys.exit(f"No encuentro {a.clip}.")
    base = os.path.splitext(a.clip)[0]
    if a.orden == "hoja":
        hoja(a.clip, a.cada, a.salida or base + "_hoja.png")
    elif a.orden == "transcribir":
        transcribir(a.clip, a.idioma, a.salida or base + "_transcripcion.txt", a.modelo)
    else:
        cortar(a.clip, a.desde, a.hasta, a.nombre, a.carpeta, a.con_audio)


if __name__ == "__main__":
    main()
