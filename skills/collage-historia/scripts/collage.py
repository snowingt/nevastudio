"""Piezas de papel para el collage: recortes, cinta, pegatinas, sellos, etiquetas, iconos y fondo.

Todo se dibuja con Pillow y numpy. Cada función devuelve una imagen RGBA lista para pegar.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

from comun import fuente, hexrgb, ancho_texto, parte_lineas, W, H

SS = 2  # supermuestreo para bordes suaves


def _rng(semilla):
    return np.random.default_rng(abs(hash(str(semilla))) % (2 ** 32))


def grano(w, h, semilla, fuerza=10):
    r = _rng(("grano", semilla, w, h))
    g = r.normal(0, fuerza, (h // 2 + 1, w // 2 + 1)).astype(np.float32)
    g = np.kron(g, np.ones((2, 2), np.float32))[:h, :w]
    return g


def borde_rasgado(w, h, semilla, amp=5.0, paso=9, lados="nseo"):
    """Máscara L con los bordes rasgados (como papel cortado a mano)."""
    r = _rng(("rasgado", semilla, w, h))
    pts = []

    def tramo(x0, y0, x1, y1, lado):
        largo = math.hypot(x1 - x0, y1 - y0)
        n = max(2, int(largo / paso))
        for i in range(n):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if lado in lados:
                d = r.uniform(0, amp)
                if lado == "n": y += d
                if lado == "s": y -= d
                if lado == "o": x += d
                if lado == "e": x -= d
            pts.append((x, y))

    tramo(0, 0, w, 0, "n"); tramo(w, 0, w, h, "e"); tramo(w, h, 0, h, "s"); tramo(0, h, 0, 0, "o")
    m = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(m).polygon([(x * SS, y * SS) for x, y in pts], fill=255)
    return m.resize((w, h), Image.LANCZOS)


def papel(w, h, color, semilla=0, rasgado=True, textura=6, lados="nseo", amp=5.0):
    w, h = int(w), int(h)
    base = np.zeros((h, w, 3), np.float32) + np.array(hexrgb(color), np.float32)
    if textura:
        base += grano(w, h, semilla, textura)[..., None]
        # fibras suaves
        fib = _rng(("fib", semilla)).normal(0, 1, (h, w // 40 + 1))
        fib = np.repeat(fib, 40, axis=1)[:, :w]
        base += fib[..., None] * 2.0
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    if rasgado:
        img.putalpha(borde_rasgado(w, h, semilla, amp=amp, lados=lados))
    return img


def con_sombra(img, dx=10, dy=12, color="#0E1B33", alfa=0.32, desenfoque=0):
    """Sombra dura desplazada. Devuelve la imagen nueva (más grande) y el desplazamiento del original."""
    w, h = img.size
    out = Image.new("RGBA", (w + abs(dx) + 4, h + abs(dy) + 4), (0, 0, 0, 0))
    a = img.getchannel("A").point(lambda v: int(v * alfa))
    sombra = Image.new("RGBA", img.size, hexrgb(color, 0))
    sombra.putalpha(a)
    if desenfoque:
        sombra = sombra.filter(ImageFilter.GaussianBlur(desenfoque))
    ox, oy = max(0, -dx) + 2, max(0, -dy) + 2
    out.alpha_composite(sombra, (ox + dx, oy + dy))
    out.alpha_composite(img, (ox, oy))
    return out, (ox, oy)


def pega(base, img, x, y):
    """Pega una imagen RGBA sobre base (RGB o RGBA) aunque se salga por los bordes."""
    x, y = int(round(x)), int(round(y))
    if x >= base.width or y >= base.height or x + img.width <= 0 or y + img.height <= 0:
        return
    base.paste(img, (x, y), img)


def rota(img, ang):
    if abs(ang) < 0.01:
        return img
    return img.rotate(ang, resample=Image.BICUBIC, expand=True)


def cinta(ancho=150, alto=44, semilla=0, color="#F3E7C9"):
    t = papel(ancho, alto, color, semilla=("cinta", semilla), rasgado=True, textura=4, lados="eo", amp=7)
    a = np.array(t.getchannel("A"), np.float32) * 0.72
    t.putalpha(Image.fromarray(a.astype(np.uint8)))
    return t


def pegatina(img, borde=12, color="#FFFFFF", contorno="#0E1B33", grosor=3):
    """Recorte fino con borde blanco de pegatina y una línea fina alrededor."""
    img = img.convert("RGBA")
    pad = borde + grosor + 4
    w, h = img.size
    lienzo = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    lienzo.alpha_composite(img, (pad, pad))
    a = lienzo.getchannel("A").point(lambda v: 255 if v > 90 else 0)
    def crece(m, r):
        # dilatación circular aproximada por varias pasadas de MaxFilter
        k = 3
        for _ in range(max(1, r // 1)):
            m = m.filter(ImageFilter.MaxFilter(k))
        return m
    a_borde = crece(a, borde).filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 110 else 0)
    a_cont = crece(a_borde, grosor).filter(ImageFilter.GaussianBlur(0.8))
    out = Image.new("RGBA", lienzo.size, hexrgb(contorno, 0))
    out.putalpha(a_cont)
    blanco = Image.new("RGBA", lienzo.size, hexrgb(color, 0))
    blanco.putalpha(a_borde.filter(ImageFilter.GaussianBlur(0.8)))
    out.alpha_composite(blanco)
    out.alpha_composite(lienzo)
    return out


def quita_fondo(img, tolerancia=40):
    """Si la imagen no tiene transparencia, quita un fondo liso (el color de las esquinas)."""
    img = img.convert("RGBA")
    a = np.array(img)
    if a[..., 3].min() < 250:
        return img
    esquinas = np.array([a[0, 0, :3], a[0, -1, :3], a[-1, 0, :3], a[-1, -1, :3]], np.float32)
    ref = np.median(esquinas, axis=0)
    if np.abs(esquinas - ref).max() > 30:
        return img  # el fondo no es liso: se deja como foto rectangular
    d = np.sqrt(((a[..., :3].astype(np.float32) - ref) ** 2).sum(axis=2))
    alfa = np.clip((d - tolerancia * 0.5) / (tolerancia * 0.5), 0, 1) * 255
    a[..., 3] = alfa.astype(np.uint8)
    return Image.fromarray(a, "RGBA").filter(ImageFilter.SMOOTH)


# ------------------------------------------------------------------ texto en papel
VARIANTES = [("papel", "texto"), ("acento", "papel"), ("texto", "papel"), ("periodico", "texto"), ("papel", "acento")]


def recorte_texto(texto, tam, c, variante=0, semilla=0, fuente_n="black", pad=(22, 10)):
    fondo, tinta = VARIANTES[variante % len(VARIANTES)]
    f = fuente(fuente_n, tam)
    x0, y0, x1, y1 = f.getbbox(texto)
    w, h = x1 - x0 + 2 * pad[0], y1 - y0 + 2 * pad[1]
    p = papel(w, h, c[fondo], semilla=("rt", texto, semilla), amp=4)
    d = ImageDraw.Draw(p)
    d.text((pad[0] - x0, pad[1] - y0), texto, font=f, fill=hexrgb(c[tinta]))
    return p


def etiqueta(texto, c, tam=46, fondo="papel", tinta="texto", semilla=0, ancho_max=560, fuente_n="bold"):
    f = fuente(fuente_n, tam)
    lineas = parte_lineas(texto, f, ancho_max)
    alto_l = int(tam * 1.18)
    w = max(ancho_texto(l, f) for l in lineas) + 56
    h = alto_l * len(lineas) + 34
    p = papel(w, h, c.get(fondo, fondo), semilla=("et", texto, semilla), amp=4)
    d = ImageDraw.Draw(p)
    for i, l in enumerate(lineas):
        x0, y0, _, _ = f.getbbox(l)
        d.text(((w - ancho_texto(l, f)) / 2 - x0, 17 + i * alto_l - y0 + (alto_l - tam) * 0.3), l, font=f,
               fill=hexrgb(c.get(tinta, tinta)))
    return p


def nota(texto, c, tam=44, semilla=0, ancho=380, color="#FFE27A"):
    f = fuente("cursiva", tam)
    lineas = parte_lineas(texto, f, ancho - 50)
    alto_l = int(tam * 1.25)
    h = max(ancho * 0.75, alto_l * len(lineas) + 70)
    p = papel(ancho, int(h), color, semilla=("nota", semilla), rasgado=False, textura=4)
    d = ImageDraw.Draw(p)
    d.rectangle([0, 0, ancho, 22], fill=hexrgb(color) + (255,))
    y = (h - alto_l * len(lineas)) / 2
    for l in lineas:
        d.text(((ancho - ancho_texto(l, f)) / 2, y), l, font=f, fill=hexrgb(c["texto"]))
        y += alto_l
    return p


def sello(texto, color, tam=78, semilla=0):
    f = fuente("black", tam)
    x0, y0, x1, y1 = f.getbbox(texto)
    tw, th = x1 - x0, y1 - y0
    w, h = tw + 90, th + 70
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = hexrgb(color, 255)
    d.rounded_rectangle([6 * SS, 6 * SS, (w - 6) * SS, (h - 6) * SS], radius=14 * SS, outline=col, width=9 * SS)
    d.rounded_rectangle([20 * SS, 20 * SS, (w - 20) * SS, (h - 20) * SS], radius=8 * SS, outline=col, width=3 * SS)
    fs = fuente("black", tam * SS)
    d.text(((w * SS - tw * SS) / 2 - x0 * SS, (h * SS - th * SS) / 2 - y0 * SS), texto, font=fs, fill=col)
    img = img.resize((w, h), Image.LANCZOS)
    # tinta gastada
    g = grano(w, h, ("sello", semilla), 60)
    a = np.array(img.getchannel("A"), np.float32)
    a = np.where(g > 55, a * 0.25, a) * 0.92
    img.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
    return img


def precio(texto, c, tam=58, semilla=0):
    f = fuente("black", tam)
    tw = ancho_texto(texto, f)
    w, h = tw + 130, int(tam * 1.9)
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(0, h / 2), (h / 2, 0), (w, 0), (w, h), (h / 2, h)]
    d.polygon([(x * SS, y * SS) for x, y in pts], fill=hexrgb(c["acento"], 255))
    d.ellipse([(h / 2 - 14) * SS, (h / 2 - 14) * SS, (h / 2 + 14) * SS, (h / 2 + 14) * SS], fill=(0, 0, 0, 0))
    d.ellipse([(h / 2 - 14) * SS, (h / 2 - 14) * SS, (h / 2 + 14) * SS, (h / 2 + 14) * SS],
              outline=hexrgb(c["papel"], 255), width=5 * SS)
    fs = fuente("black", tam * SS)
    x0, y0, x1, y1 = fs.getbbox(texto)
    d.text(((h / 2 + 34) * SS - x0, (h * SS - (y1 - y0)) / 2 - y0), texto, font=fs, fill=hexrgb(c["papel"], 255))
    return img.resize((w, h), Image.LANCZOS)


def palabra_caja(texto, c, tam=150, ancho_max=980):
    f = fuente("black", tam)
    while ancho_texto(texto, f) > ancho_max - 80 and tam > 40:
        tam -= 6; f = fuente("black", tam)
    x0, y0, x1, y1 = f.getbbox(texto)
    w, h = x1 - x0 + 80, y1 - y0 + 60
    p = papel(w, h, c["acento"], semilla=("pc", texto), amp=5)
    ImageDraw.Draw(p).text((40 - x0, 30 - y0), texto, font=f, fill=hexrgb("#FFFFFF"))
    return p


def polaroid(w_foto, h_foto, pie=None, c=None, semilla=0):
    m, abajo = 22, (78 if pie else 26)
    w, h = w_foto + 2 * m, h_foto + m + abajo
    p = papel(w, h, c["papel"] if c else "#FBF7EE", semilla=("pol", semilla), rasgado=False, textura=3)
    if pie:
        tam = 34
        f = fuente("cursiva", tam)
        while ancho_texto(pie, f) > w - 40 and tam > 22:
            tam -= 2; f = fuente("cursiva", tam)
        texto = pie
        while ancho_texto(texto, f) > w - 40 and len(texto) > 4:
            texto = texto[:-2] + "…" if not texto.endswith("…") else texto[:-3] + "…"
        ImageDraw.Draw(p).text(((w - ancho_texto(texto, f)) / 2, h_foto + m + 14), texto, font=f,
                               fill=hexrgb(c["texto"] if c else "#0E1B33"))
    return p, (m, m)


def cuadriculado(w, h, c, semilla=0):
    p = papel(w, h, "#F7F6F0", semilla=("cuad", semilla), amp=4, textura=3)
    d = ImageDraw.Draw(p)
    azul = (120, 160, 210, 120)
    for x in range(0, w, 28):
        d.line([(x, 0), (x, h)], fill=azul, width=1)
    for y in range(0, h, 28):
        d.line([(0, y), (w, y)], fill=azul, width=1)
    return p


def tarjeta_reel(w, h, c, semilla=0, img=None):
    """Miniatura de un reel cualquiera: todas iguales a propósito."""
    p = papel(w, h, "#FFFFFF", semilla=("tr", semilla), rasgado=False, textura=2)
    d = ImageDraw.Draw(p)
    d.rounded_rectangle([3, 3, w - 4, h - 4], radius=max(4, w // 10), outline=hexrgb(c["texto"]), width=max(2, w // 40))
    if img is not None:
        mini = img.convert("RGB").resize((w - 16, int(h * 0.55)))
        p.paste(mini, (8, 8))
    else:
        d.rectangle([8, 8, w - 9, int(h * 0.55) + 8], fill=hexrgb(c["fondo"]))
    cx, cy, r = w // 2, int(h * 0.3), max(5, w // 7)
    d.polygon([(cx - r * 0.6, cy - r), (cx - r * 0.6, cy + r), (cx + r, cy)], fill=hexrgb(c["acento"]))
    for i in range(3):
        y = int(h * 0.68) + i * max(5, h // 12)
        d.rounded_rectangle([10, y, w - 10 - i * w // 5, y + max(3, h // 30)], radius=2, fill=hexrgb(c["texto"]))
    return p


def tachon(w, h, color, progreso=1.0, grosor=22, semilla=0):
    """Garabato de tachado en X que se dibuja según el progreso (0–1)."""
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = _rng(("tach", semilla))
    trazos = [((0.05, 0.1), (0.95, 0.9)), ((0.92, 0.08), (0.08, 0.92))]
    total = len(trazos)
    for k, (a, b) in enumerate(trazos):
        p = max(0.0, min(1.0, progreso * total - k))
        if p <= 0:
            continue
        n = 24
        pts = []
        for i in range(int(n * p) + 1):
            t = i / n
            x = a[0] + (b[0] - a[0]) * t + r.uniform(-0.01, 0.01)
            y = a[1] + (b[1] - a[1]) * t + math.sin(t * 9) * 0.012
            pts.append((x * w * SS, y * h * SS))
        if len(pts) > 1:
            d.line(pts, fill=hexrgb(color, 235), width=grosor * SS, joint="curve")
    return img.resize((w, h), Image.LANCZOS)


# ------------------------------------------------------------------ iconos dibujados (propios)
ICONOS = ["lapiz", "tijeras", "codigo", "microfono", "botas", "libro", "claqueta", "mando", "regalo", "estrella",
          "flecha", "check", "cruz", "rayo", "bombilla", "corazon", "reloj", "bocadillo", "cohete", "ojo", "camara",
          "dinero", "trofeo", "mundo"]


def icono(nombre, tam, c, color=None):
    if nombre not in ICONOS:
        raise ValueError(f"icono «{nombre}» no existe. Hay: {', '.join(ICONOS)}")
    S = 400
    img = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    k = SS
    L = hexrgb(c["texto"], 255)
    A = hexrgb(color or c["acento"], 255)
    B = hexrgb(c["papel"], 255)
    G = 14 * k  # grosor de línea

    def P(*pts):
        return [(x * k, y * k) for x, y in pts]

    def rect(x0, y0, x1, y1, fill, r=0):
        d.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=r * k, fill=fill, outline=L, width=G)

    def elip(x0, y0, x1, y1, fill):
        d.ellipse([x0 * k, y0 * k, x1 * k, y1 * k], fill=fill, outline=L, width=G)

    def poli(pts, fill):
        d.polygon(P(*pts), fill=fill, outline=L, width=G)

    def linea(pts, w=None, col=None):
        d.line(P(*pts), fill=col or L, width=w or G, joint="curve")

    if nombre == "lapiz":
        poli([(90, 300), (270, 120), (320, 170), (140, 350), (80, 360)], A)
        poli([(80, 360), (90, 300), (140, 350)], B)
        linea([(250, 140), (300, 190)])
    elif nombre == "tijeras":
        elip(70, 230, 160, 320, B); elip(170, 270, 260, 360, B)
        poli([(140, 245), (330, 70), (345, 90), (175, 270)], A)
        poli([(205, 280), (330, 140), (345, 160), (220, 300)], A)
    elif nombre == "codigo":
        rect(50, 80, 350, 320, B, 22)
        linea([(150, 150), (100, 200), (150, 250)], 18 * k, A)
        linea([(250, 150), (300, 200), (250, 250)], 18 * k, A)
        linea([(220, 140), (180, 260)])
    elif nombre == "microfono":
        rect(150, 50, 250, 230, A, 50)
        linea([(110, 180), (110, 210), (140, 260), (200, 280), (260, 260), (290, 210), (290, 180)])
        linea([(200, 280), (200, 340)]); linea([(140, 345), (260, 345)])
    elif nombre == "botas":
        # bota cohete propia: caña alta, puntera redonda, suela clara y llama bajo el talón
        poli([(140, 318), (255, 318), (240, 398), (198, 362), (155, 398)], hexrgb("#FFD23F", 255))
        poli([(110, 60), (215, 60), (220, 205), (300, 215), (335, 250), (335, 300), (105, 300)], A)
        d.rounded_rectangle([96 * k, 290 * k, 345 * k, 325 * k], radius=12 * k, fill=B, outline=L, width=G)
        d.rounded_rectangle([102 * k, 48 * k, 225 * k, 92 * k], radius=10 * k, fill=B, outline=L, width=G)
        linea([(112, 150), (215, 150)], 10 * k); linea([(240, 230), (262, 262)], 10 * k)
    elif nombre == "libro":
        poli([(60, 110), (200, 140), (200, 330), (60, 300)], A)
        poli([(340, 110), (200, 140), (200, 330), (340, 300)], B)
        for y in (180, 220, 260):
            linea([(230, y), (310, y - 8)], 8 * k)
    elif nombre == "claqueta":
        rect(70, 170, 330, 330, B, 10)
        poli([(70, 120), (320, 75), (330, 125), (80, 170)], L)
        for x in (110, 170, 230, 290):
            linea([(x, 162 - (x - 70) * 0.18), (x + 30, 112 - (x - 70) * 0.18)], 14 * k, B)
    elif nombre == "mando":
        rect(140, 50, 260, 350, B, 30)
        elip(175, 85, 225, 135, A)
        for y in (180, 230, 280):
            for x in (170, 230):
                d.ellipse([(x - 12) * k, (y - 12) * k, (x + 12) * k, (y + 12) * k], fill=L)
    elif nombre == "regalo":
        rect(70, 170, 330, 340, A, 8)
        rect(55, 120, 345, 180, A, 8)
        d.rectangle([180 * k, 120 * k, 220 * k, 340 * k], fill=B, outline=L, width=G // 2)
        elip(130, 60, 200, 125, B); elip(200, 60, 270, 125, B)
    elif nombre == "estrella":
        pts = [(200 + 160 * math.cos(math.radians(-90 + i * 36)) * (1 if i % 2 == 0 else 0.45),
                205 + 160 * math.sin(math.radians(-90 + i * 36)) * (1 if i % 2 == 0 else 0.45)) for i in range(10)]
        poli(pts, A)
    elif nombre == "flecha":
        poli([(50, 160), (230, 160), (230, 90), (350, 200), (230, 310), (230, 240), (50, 240)], A)
    elif nombre == "check":
        linea([(80, 210), (165, 295), (330, 105)], 44 * k, A)
    elif nombre == "cruz":
        linea([(90, 90), (310, 310)], 44 * k, hexrgb(c["rojo"], 255)); linea([(310, 90), (90, 310)], 44 * k, hexrgb(c["rojo"], 255))
    elif nombre == "rayo":
        poli([(230, 40), (100, 220), (190, 220), (160, 360), (300, 170), (210, 170)], A)
    elif nombre == "bombilla":
        elip(110, 50, 290, 240, hexrgb("#FFD23F", 255))
        rect(155, 240, 245, 310, B, 8); linea([(160, 335), (240, 335)])
    elif nombre == "corazon":
        poli([(200, 340), (70, 200), (70, 120), (130, 70), (200, 110), (270, 70), (330, 120), (330, 200)], A)
    elif nombre == "reloj":
        elip(60, 60, 340, 340, B); linea([(200, 200), (200, 110)]); linea([(200, 200), (265, 235)], 14 * k, A)
    elif nombre == "bocadillo":
        rect(50, 70, 350, 270, B, 40); poli([(120, 260), (110, 340), (190, 265)], B)
        for x in (140, 200, 260):
            d.ellipse([(x - 16) * k, 154 * k, (x + 16) * k, 186 * k], fill=A)
    elif nombre == "cohete":
        poli([(200, 40), (260, 130), (260, 280), (140, 280), (140, 130)], B)
        elip(170, 130, 230, 190, A)
        poli([(140, 220), (90, 300), (140, 290)], A); poli([(260, 220), (310, 300), (260, 290)], A)
        poli([(165, 285), (235, 285), (200, 370)], hexrgb("#FFD23F", 255))
    elif nombre == "ojo":
        poli([(40, 200), (120, 120), (200, 95), (280, 120), (360, 200), (280, 280), (200, 305), (120, 280)], B)
        elip(145, 145, 255, 255, A); d.ellipse([180 * k, 180 * k, 220 * k, 220 * k], fill=L)
    elif nombre == "camara":
        rect(50, 120, 350, 320, B, 24); rect(140, 80, 260, 125, B, 10); elip(130, 150, 270, 290, A)
    elif nombre == "dinero":
        rect(50, 110, 350, 290, hexrgb("#9BD18B", 255), 16); elip(150, 150, 250, 250, B)
        linea([(200, 170), (200, 230)], 12 * k)
    elif nombre == "trofeo":
        poli([(110, 70), (290, 70), (270, 200), (200, 240), (130, 200)], hexrgb("#FFD23F", 255))
        rect(170, 240, 230, 300, A, 4); rect(120, 300, 280, 345, B, 6)
    elif nombre == "mundo":
        elip(60, 60, 340, 340, hexrgb("#8EC5E8", 255))
        poli([(120, 120), (190, 110), (200, 180), (140, 210), (100, 170)], hexrgb("#9BD18B", 255))
        poli([(230, 220), (300, 200), (310, 260), (250, 300)], hexrgb("#9BD18B", 255))
    img = img.resize((S, S), Image.LANCZOS)
    bb = img.getbbox()
    if bb:
        img = img.crop(bb)
    f = tam / max(img.size)
    return img.resize((max(1, int(img.width * f)), max(1, int(img.height * f))), Image.LANCZOS)


# ------------------------------------------------------------------ fondo y tira de película
def fondo(c, semilla=0, decorado=True):
    base = np.zeros((H, W, 3), np.float32) + np.array(hexrgb(c["fondo"]), np.float32)
    base += grano(W, H, ("fondo", semilla), 7)[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    vign = ((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2
    base *= (1 - 0.18 * np.clip(vign, 0, 1))[..., None]
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    if decorado:
        r = _rng(("deco", semilla))
        # trozos de papel de periódico y puntos de trama en los bordes, muy suaves
        for i in range(7):
            w, h = int(r.uniform(160, 340)), int(r.uniform(90, 220))
            p = papel(w, h, c["periodico"], semilla=("deco", i, semilla), amp=7, textura=5)
            d = ImageDraw.Draw(p)
            for y in range(14, h - 10, 16):
                d.line([(14, y), (w - 14 - int(r.uniform(0, 60)), y)], fill=(90, 90, 90, 60), width=5)
            a = np.array(p.getchannel("A"), np.float32) * 0.55
            p.putalpha(Image.fromarray(a.astype(np.uint8)))
            p = rota(p, r.uniform(-20, 20))
            lado = i % 2
            x = int(r.uniform(-120, 60)) if lado == 0 else int(W - p.width + r.uniform(-60, 120))
            y = int(r.uniform(0, H - p.height))
            pega(img, p, x, y)
        trama = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(trama)
        for (cx, cy) in [(W - 60, 260), (70, 1250)]:
            for yy2 in range(-150, 151, 22):
                for xx2 in range(-150, 151, 22):
                    rr = 7 * max(0, 1 - math.hypot(xx2, yy2) / 160)
                    if rr > 0.8:
                        d.ellipse([cx + xx2 - rr, cy + yy2 - rr, cx + xx2 + rr, cy + yy2 + rr], fill=hexrgb(c["acento"], 70))
        img.alpha_composite(trama)
    return img.convert("RGB")


def tira_pelicula(miniaturas, alto, c):
    """Tira de película horizontal con las miniaturas dadas (se repite en bucle al moverse)."""
    if not miniaturas:
        miniaturas = [Image.new("RGB", (16, 9), hexrgb(c["acento"]))]
    hueco = int(alto * 0.62)
    celdas = []
    for m in miniaturas:
        f = hueco / m.height
        celdas.append(m.convert("RGB").resize((max(1, int(m.width * f)), hueco)))
    sep = 18
    ancho = sum(cel.width + sep for cel in celdas)
    while ancho < W + 400:
        celdas = celdas + celdas
        ancho = sum(cel.width + sep for cel in celdas)
    tira = Image.new("RGBA", (ancho, alto), hexrgb("#15161A", 255))
    d = ImageDraw.Draw(tira)
    x = 0
    y0 = (alto - hueco) // 2
    for cel in celdas:
        tira.paste(cel, (x + sep // 2, y0))
        x += cel.width + sep
    agujero = int(alto * 0.09)
    for xx in range(10, ancho, agujero * 2 + 6):
        for yy in (int(alto * 0.07), alto - int(alto * 0.07) - agujero):
            d.rounded_rectangle([xx, yy, xx + agujero * 1.3, yy + agujero], radius=3, fill=hexrgb(c["fondo"], 255))
    return tira
