#!/usr/bin/env python3
"""Crea el material del ejemplo (clips, recortes y un narrador de papel), todo dibujado con código.

Uso:  python3 ejemplo/crear_ejemplo.py proyectos/prueba
Así el ejemplo funciona sin material de nadie: sirve para comprobar que todo va bien antes de usar tus clips.
"""
import math, os, subprocess, sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from comun import FFMPEG  # noqa: E402

TINTA = (14, 27, 51)


def liebre(d, x, y, s=1.0, fase=0.0):
    pata = math.sin(fase) * 14 * s
    d.ellipse([x - 60 * s, y - 30 * s, x + 50 * s, y + 30 * s], fill=(196, 160, 120), outline=TINTA, width=int(5 * s))
    d.ellipse([x + 30 * s, y - 55 * s, x + 85 * s, y - 5 * s], fill=(196, 160, 120), outline=TINTA, width=int(5 * s))
    d.ellipse([x + 38 * s, y - 120 * s, x + 56 * s, y - 45 * s], fill=(214, 182, 145), outline=TINTA, width=int(4 * s))
    d.ellipse([x + 55 * s, y - 115 * s, x + 73 * s, y - 42 * s], fill=(214, 182, 145), outline=TINTA, width=int(4 * s))
    d.ellipse([x + 62 * s, y - 38 * s, x + 72 * s, y - 28 * s], fill=TINTA)
    d.line([(x - 30 * s, y + 25 * s), (x - 45 * s - pata, y + 55 * s)], fill=TINTA, width=int(8 * s))
    d.line([(x + 25 * s, y + 25 * s), (x + 40 * s + pata, y + 55 * s)], fill=TINTA, width=int(8 * s))


def tortuga(d, x, y, s=1.0, fase=0.0):
    pata = math.sin(fase) * 6 * s
    d.ellipse([x + 45 * s, y - 25 * s, x + 90 * s, y + 15 * s], fill=(140, 190, 110), outline=TINTA, width=int(5 * s))
    d.ellipse([x + 70 * s, y - 12 * s, x + 78 * s, y - 4 * s], fill=TINTA)
    for px in (-35, 25):
        d.ellipse([x + (px + pata) * s, y + 15 * s, x + (px + 22 + pata) * s, y + 45 * s], fill=(140, 190, 110), outline=TINTA, width=int(4 * s))
    d.chord([x - 60 * s, y - 55 * s, x + 60 * s, y + 55 * s], 180, 360, fill=(90, 130, 70), outline=TINTA, width=int(6 * s))
    d.line([(x - 60 * s, y), (x + 60 * s, y)], fill=TINTA, width=int(6 * s))
    for hx in (-25, 10):
        d.polygon([(x + hx * s, y - 12 * s), (x + (hx + 15) * s, y - 35 * s), (x + (hx + 30) * s, y - 12 * s)], outline=TINTA, width=int(3 * s))


def escena(n, w=480, h=270):
    img = Image.new("RGB", (w, h), (160, 205, 235))
    d = ImageDraw.Draw(img)
    d.rectangle([0, h * 0.62, w, h], fill=(120, 180, 90))
    d.ellipse([w * 0.75, 20, w * 0.75 + 50, 70], fill=(255, 215, 80))
    return img, d


def clip(ruta, dibuja, segundos=4.0):
    n = int(segundos * 30)
    pr = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "480x270", "-r", "30",
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", ruta], stdin=subprocess.PIPE)
    for k in range(n):
        img, d = escena(k)
        dibuja(d, k / 30.0)
        pr.stdin.write(img.tobytes())
    pr.stdin.close(); pr.wait()


def recorte(ruta, fn):
    img = Image.new("RGBA", (300, 260), (0, 0, 0, 0))
    fn(ImageDraw.Draw(img), 120, 170, 1.4, 0.0)
    img.crop(img.getbbox()).save(ruta)


def narrador(ruta, pose):
    img = Image.new("RGBA", (420, 640), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([110, 300, 310, 600], radius=40, fill=(76, 120, 200), outline=TINTA, width=8)
    if pose == "pulgar":
        d.line([(300, 360), (370, 300)], fill=TINTA, width=26); d.ellipse([350, 250, 400, 300], fill=(255, 214, 170), outline=TINTA, width=6)
        d.line([(120, 360), (70, 470)], fill=TINTA, width=26)
    elif pose == "sorpresa":
        d.line([(300, 360), (370, 240)], fill=TINTA, width=26); d.line([(120, 360), (50, 240)], fill=TINTA, width=26)
    else:
        d.line([(300, 360), (350, 480)], fill=TINTA, width=26); d.line([(120, 360), (70, 480)], fill=TINTA, width=26)
    d.ellipse([90, 60, 330, 300], fill=(255, 214, 170), outline=TINTA, width=8)
    d.pieslice([90, 40, 330, 230], 180, 360, fill=(120, 70, 40), outline=TINTA, width=8)
    ojo = 26 if pose == "sorpresa" else 18
    for ex in (165, 255):
        d.ellipse([ex - ojo / 2, 170 - ojo / 2, ex + ojo / 2, 170 + ojo / 2], fill=TINTA)
    if pose == "sorpresa":
        d.ellipse([190, 215, 230, 260], fill=TINTA)
    else:
        d.arc([170, 190, 250, 250], 20, 160, fill=TINTA, width=8)
    img.save(ruta)


def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: python3 ejemplo/crear_ejemplo.py CARPETA_DEL_PROYECTO")
    p = sys.argv[1]
    for sub in ("clips", "imagenes", "personaje"):
        os.makedirs(os.path.join(p, sub), exist_ok=True)
    clip(os.path.join(p, "clips", "liebre_corre.mp4"), lambda d, t: liebre(d, -80 + t * 160, 185, 1.0, t * 18))
    clip(os.path.join(p, "clips", "liebre_duerme.mp4"),
         lambda d, t: (liebre(d, 240, 190, 1.0, 0), d.text((300, 90 - (t * 12 % 30)), "z z z", fill=TINTA)))
    clip(os.path.join(p, "clips", "tortuga_meta.mp4"),
         lambda d, t: (d.rectangle([400, 110, 410, 230], fill=TINTA), d.rectangle([410, 110, 460, 140], fill=(255, 122, 26)),
                       tortuga(d, 60 + t * 75, 195, 1.0, t * 6)))
    recorte(os.path.join(p, "imagenes", "liebre.png"), liebre)
    recorte(os.path.join(p, "imagenes", "tortuga.png"), tortuga)
    for pose in ("normal", "sorpresa", "pulgar"):
        narrador(os.path.join(p, "personaje", f"{pose}.png"), pose)
    print("Material del ejemplo creado en", p)


if __name__ == "__main__":
    main()
