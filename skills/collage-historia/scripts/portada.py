#!/usr/bin/env python3
"""Portada en collage (1080×1920, la misma para Instagram y TikTok).

Uso:  python3 scripts/portada.py P/video.json
Lee "portada" de video.json:
  {"etiqueta": "SKILL DE CLAUDE", "linea": "un villano lo predijo", "grande": "2004", "remate": "y ya está pasando",
   "imagen": "clave de imagenes" | "clip": "clave de clips", "pose": "pose del personaje"}
Deja P/salida/portada.png y P/salida/portada_comprobar.png (el recorte 3:4 que enseña la cuadrícula del perfil
y cómo se ve a 120 px de ancho). Todo lo importante queda dentro de y = 240–1680.
"""
import argparse, os, subprocess, sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import FFMPEG, W, H, estilo, cargar_json, fuente, ancho_texto  # noqa: E402
import collage as cg  # noqa: E402

Y0, Y1 = 240, 1680


def recortes_linea(texto, tam, c, ancho_max, semilla, variantes=(0, 2, 3)):
    palabras = texto.split()
    while True:
        imgs = [cg.recorte_texto(p.replace("**", ""), tam, c, 1 if p.startswith("**") else variantes[k % len(variantes)],
                                 semilla=(semilla, k)) for k, p in enumerate(palabras)]
        total = sum(im.width for im in imgs) - 8 * (len(imgs) - 1)
        if total <= ancho_max or tam < 40:
            return imgs, total
        tam -= 6


def pega_linea(lienzo, imgs, total, cx, y, c):
    x = cx - total / 2
    for k, im in enumerate(imgs):
        r = cg._rng(("por", y, k))
        sp, _ = cg.con_sombra(cg.rota(im, r.uniform(-4, 4)), 7, 8, color=c["sombra"], alfa=0.3)
        cg.pega(lienzo, sp, x, y - sp.height / 2)
        x += im.width - 8


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    a = ap.parse_args()
    plan_dir = os.path.dirname(os.path.abspath(a.plan))
    plan = cargar_json(a.plan)
    cfg = plan.get("portada")
    if not cfg:
        sys.exit("Añade \"portada\" en video.json (etiqueta, linea, grande, remate, imagen o clip y pose).")
    c = estilo(plan)
    lienzo = cg.fondo(c, semilla=plan.get("semilla", 1) + 7).convert("RGBA")

    # imagen o fotograma del clip, abajo a la derecha
    foto = None
    if cfg.get("imagen"):
        ruta = plan.get("imagenes", {}).get(cfg["imagen"], cfg["imagen"])
        foto = cg.quita_fondo(Image.open(os.path.join(plan_dir, ruta)))
        foto = foto.resize((440, int(foto.height * 440 / foto.width)), Image.LANCZOS)
        if foto.height > 620:
            foto = foto.resize((int(foto.width * 620 / foto.height), 620), Image.LANCZOS)
        foto = cg.pegatina(foto, borde=12, color=c["papel"], contorno=c["texto"], grosor=3)
    elif cfg.get("clip"):
        ruta = os.path.join(plan_dir, plan.get("clips", {}).get(cfg["clip"], cfg["clip"]))
        raw = subprocess.run([FFMPEG, "-v", "error", "-ss", str(cfg.get("segundo", 1.0)), "-i", ruta, "-frames:v", "1",
                              "-vf", "scale=480:-2", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
        import io
        fr = Image.open(io.BytesIO(raw)).convert("RGBA")
        marco, (mx, my) = cg.polaroid(fr.width, fr.height, plan.get("fuente_clips"), c, "portada")
        marco.alpha_composite(fr, (mx, my))
        foto = marco
    if foto is not None:
        sp, _ = cg.con_sombra(cg.rota(foto, -6), 12, 14, color=c["sombra"])
        cg.pega(lienzo, sp, W - sp.width - 30, Y1 - sp.height - 10)

    # personaje grande, abajo a la izquierda, con su halo
    pers = plan.get("personaje")
    if pers:
        carpeta = pers["carpeta"] if os.path.isabs(pers["carpeta"]) else os.path.join(plan_dir, pers["carpeta"])
        pose = cfg.get("pose", pers.get("pose"))
        candidatos = [f for f in sorted(os.listdir(carpeta)) if f.lower().endswith((".png", ".webp"))]
        elegido = next((f for f in candidatos if os.path.splitext(f)[0] == pose), candidatos[0] if candidatos else None)
        if elegido:
            img = cg.quita_fondo(Image.open(os.path.join(carpeta, elegido)))
            img = img.crop(img.getbbox())
            alto = 760
            img = img.resize((int(img.width * alto / img.height), alto), Image.LANCZOS)
            if img.width > 560:
                img = img.resize((560, int(img.height * 560 / img.width)), Image.LANCZOS)
            img = cg.pegatina(img, borde=9, color=c["papel"], contorno=c["texto"], grosor=3)
            halo = Image.new("RGBA", (560, 560), (0, 0, 0, 0))
            ImageDraw.Draw(halo).ellipse([0, 0, 560, 560], fill=tuple(int(c["acento"][i:i + 2], 16) for i in (1, 3, 5)) + (255,))
            cg.pega(lienzo, halo, 250 - 280, Y1 - img.height * 0.7 - 280)
            cg.pega(lienzo, img, 250 - img.width / 2, Y1 + 120 - img.height)

    # textos, de arriba abajo
    y = Y0 + 70
    if cfg.get("etiqueta"):
        et = cg.etiqueta(cfg["etiqueta"], c, tam=58, fondo="texto", tinta="papel", semilla="por_et")
        sp, _ = cg.con_sombra(cg.rota(et, -2), 6, 7, color=c["sombra"])
        cg.pega(lienzo, sp, (W - sp.width) / 2, y - sp.height / 2)
        y += 140
    if cfg.get("linea"):
        imgs, total = recortes_linea(cfg["linea"].upper(), 96, c, 1000, "linea")
        pega_linea(lienzo, imgs, total, W / 2, y, c)
        y += 150
    if cfg.get("grande"):
        g = cg.palabra_caja(cfg["grande"], c, tam=300, ancho_max=1000)
        sp, _ = cg.con_sombra(cg.rota(g, -3), 14, 16, color=c["sombra"])
        cg.pega(lienzo, sp, (W - sp.width) / 2, y - 30)
        y += sp.height + 40
    if cfg.get("remate"):
        imgs, total = recortes_linea(cfg["remate"].upper(), 76, c, 1000, "remate", variantes=(2, 0))
        pega_linea(lienzo, imgs, total, W / 2, y, c)
        y += 120
    if y > 1150:
        print("Aviso: los textos bajan mucho y pueden tapar la cara del personaje. Acorta la línea o el remate.")

    salida = os.path.join(plan_dir, "salida")
    os.makedirs(salida, exist_ok=True)
    final = lienzo.convert("RGB")
    final.save(os.path.join(salida, "portada.png"))
    # comprobación: recorte 3:4 de la cuadrícula del perfil y miniatura de 120 px
    rec = final.crop((0, Y0, W, Y1))
    mini = rec.resize((120, 160), Image.LANCZOS)
    comp = Image.new("RGB", (rec.width // 2 + 60 + 120 * 2, rec.height // 2 + 80), (40, 40, 40))
    comp.paste(rec.resize((rec.width // 2, rec.height // 2)), (20, 60))
    comp.paste(mini.resize((240, 320), Image.NEAREST), (rec.width // 2 + 40, 60))
    d = ImageDraw.Draw(comp)
    f = fuente("bold", 22)
    d.text((20, 18), "Recorte 3:4 del perfil", font=f, fill=(240, 240, 240))
    d.text((rec.width // 2 + 40, 18), "A 120 px (ampliado)", font=f, fill=(240, 240, 240))
    comp.save(os.path.join(salida, "portada_comprobar.png"))
    print("Portada:", os.path.join(salida, "portada.png"))
    print("Comprobación:", os.path.join(salida, "portada_comprobar.png"), "· mira que el número y el título se lean a 120 px")
    _ = ancho_texto


if __name__ == "__main__":
    main()
