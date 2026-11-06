"""Mide el ritmo de un reel ya renderizado: busca los tramos en los que no pasa nada en pantalla.

Uso:
  python3 ritmo.py salida/reel.mp4 [--tiempos src/datos/tiempos.json] [--hueco 0.6] [--umbral 1.5] [--umbral-detalle 6] [--json informe.json]

Cómo mide:
  - Reduce el vídeo a 540x960 en gris y compara cada fotograma con el anterior, por zonas de pantalla
    (arriba, centro, abajo), porque un cambio pequeño en una zona se pierde en la media de toda la imagen.
  - Un fotograma "tiene evento" si en alguna zona la diferencia media pasa de --umbral (escala 0-255)
    o si en alguna baldosa de 90x80 px la diferencia con dos fotogramas antes pasa de --umbral-detalle.
    Lo primero cuenta tarjetas, iconos y cambios grandes; lo segundo, cosas pequeñas que también se ven,
    como cada palabra que aparece en los subtítulos. Los dos dejan fuera la respiración del personaje,
    el empuje lento de cámara y las manchas del fondo.
  - Un "hueco" es un tramo seguido sin eventos más largo que --hueco segundos (0,6 s es la regla del método:
    en los reels de referencia nunca pasan más de 0,6 s sin que algo cambie).
Con --tiempos dice en qué frase cae cada hueco, para saber qué escena hay que animar más.
Termina con código 1 si hay huecos, para usarlo como control antes de entregar.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np

W, H = 540, 960
ZONAS = {"arriba": (0, 300), "centro": (300, 640), "abajo": (640, 960)}


def ffmpeg_bin(video):
    """ffmpeg del sistema, el que trae Remotion en el proyecto del vídeo (salida/../node_modules) o imageio-ffmpeg."""
    if shutil.which("ffmpeg"):
        return "ffmpeg", dict(os.environ)
    proyecto = os.path.dirname(os.path.dirname(os.path.abspath(video)))
    base = os.path.join(proyecto, "node_modules", "@remotion")
    if os.path.isdir(base):
        for d in sorted(os.listdir(base)):
            b = os.path.join(base, d, "ffmpeg")
            if d.startswith("compositor-") and os.path.exists(b):
                env = dict(os.environ)
                env["LD_LIBRARY_PATH"] = os.path.join(base, d) + ":" + env.get("LD_LIBRARY_PATH", "")
                env["DYLD_LIBRARY_PATH"] = os.path.join(base, d)
                return b, env
    try:
        import imageio_ffmpeg  # type: ignore

        return imageio_ffmpeg.get_ffmpeg_exe(), dict(os.environ)
    except Exception:
        sys.exit("No encuentro ffmpeg. Instálalo con: pip install imageio-ffmpeg")


def fps_de(video, ff, env):
    out = subprocess.run([ff, "-hide_banner", "-i", video], capture_output=True, text=True, env=env).stderr
    import re

    m = re.search(r"(\d+(?:\.\d+)?) fps", out)
    return float(m.group(1)) if m else 30.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--tiempos")
    ap.add_argument("--hueco", type=float, default=0.6)
    ap.add_argument("--umbral", type=float, default=1.5)
    ap.add_argument("--umbral-detalle", type=float, default=6.0)
    ap.add_argument("--json")
    a = ap.parse_args()

    ff, env = ffmpeg_bin(a.video)
    fps = fps_de(a.video, ff, env)
    cmd = [ff, "-hide_banner", "-loglevel", "error", "-i", a.video, "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env)
    TW, TH = 90, 80
    previos = []
    difs = []
    detalle = []
    while True:
        buf = proc.stdout.read(W * H)
        if len(buf) < W * H:
            break
        fr = np.frombuffer(buf, dtype=np.uint8).reshape(H, W).astype(np.int16)
        if previos:
            d = np.abs(fr - previos[-1])
            difs.append([d[y0:y1].mean() for y0, y1 in ZONAS.values()])
            d2 = np.abs(fr - previos[0])  # dos fotogramas atrás: pilla los fundidos cortos
            detalle.append(d2.reshape(H // TH, TH, W // TW, TW).mean(axis=(1, 3)).max())
        previos = (previos + [fr])[-2:]
    proc.wait()
    if not difs:
        sys.exit("No he podido leer fotogramas del vídeo")
    difs = np.array(difs)
    evento = (difs > a.umbral).any(axis=1) | (np.array(detalle) > a.umbral_detalle)
    n = len(evento) + 1
    dur = n / fps

    huecos = []
    i = 0
    while i < len(evento):
        if not evento[i]:
            j = i
            while j < len(evento) and not evento[j]:
                j += 1
            largo = (j - i) / fps
            if largo > a.hueco:
                huecos.append((round((i + 1) / fps, 2), round((j + 1) / fps, 2), round(largo, 2)))
            i = j
        else:
            i += 1

    frases = []
    if a.tiempos:
        frases = json.load(open(a.tiempos))["frases"]

    def frase_de(t):
        for k, f in enumerate(frases):
            sig = frases[k + 1]["inicio"] if k + 1 < len(frases) else 1e9
            if f["inicio"] - 0.3 <= t < sig:
                return k, f["texto"]
        return None, ""

    quietos = 100 * (~evento).mean()
    # eventos = arranques de movimiento (fotograma con evento tras uno sin evento) + cambios fuertes
    arranques = int(((evento[1:]) & (~evento[:-1])).sum()) + int(evento[0])
    print(f"duración {dur:.2f} s · {fps:.0f} fps · fotogramas quietos {quietos:.1f} % · arranques de movimiento {arranques / dur:.2f}/s")
    if huecos:
        print(f"HUECOS de más de {a.hueco} s sin nada nuevo en pantalla: {len(huecos)}")
        for t0, t1, l in huecos:
            k, texto = frase_de(t0)
            donde = f"  ← frase {k + 1}: {texto}" if k is not None else ""
            print(f"  {t0:6.2f}–{t1:6.2f} s ({l:.2f} s){donde}")
        print("Arréglalo: haz que algo entre o cambie en ese tramo (una palabra clave que dispare un elemento, un contador, un icono).")
    else:
        print(f"OK: ningún tramo de más de {a.hueco} s sin movimiento.")
    if a.json:
        json.dump({"duracion": dur, "fps": fps, "quietos_pct": quietos, "huecos": huecos}, open(a.json, "w"), indent=1)
    sys.exit(1 if huecos else 0)


if __name__ == "__main__":
    main()
