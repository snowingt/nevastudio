#!/usr/bin/env python3
"""Monta el vídeo de collage a partir de video.json y la voz alineada.

Uso:
  python3 scripts/render.py P/video.json --muestras        # una miniatura por frase → P/salida/muestras_1.png (+ avisos)
  python3 scripts/render.py P/video.json --en 12.5         # un fotograma a tamaño real → P/salida/fotograma_12.5.png
  python3 scripts/render.py P/video.json                   # vídeo con el final normal → P/salida/<nombre>_instagram.mp4
  python3 scripts/render.py P/video.json --final tiktok    # segundo final: reutiliza el cuerpo ya hecho
  python3 scripts/render.py P/video.json --voz voz_b --sufijo b   # otra voz (por ejemplo, con las citas originales)
  python3 scripts/render.py P/video.json --rapido          # borrador a media resolución, para revisar el ritmo

El cuerpo (todo hasta la última frase) se hace por tandas de 20 s en P/salida/partes/ y se reutiliza si no ha cambiado:
si el proceso se corta, repite el mismo comando y sigue donde iba. --rehacer obliga a hacerlo todo de nuevo.
"""
import argparse, hashlib, json, math, os, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import (FFMPEG, W, H, FPS, estilo, fuente, hexrgb, normaliza, limpia, cargar_json, ancho_texto,  # noqa: E402
                   ENLACE, suave, rebote, duracion_media)
import collage as cg  # noqa: E402

ZONA_CENTRO = (40, 450, 1040, 1280)
Y_SUB = 1335
SUB_ANTES = 8 / FPS
T_ENTRA = 0.36
T_SALE = 0.18
AVISOS = []


def aviso(msg):
    if msg not in AVISOS:
        AVISOS.append(msg)


# ------------------------------------------------------------------ datos y tiempos
class Linea:
    def __init__(self, plan_dir, plan, voz_dir, final, version="a"):
        self.dir = plan_dir
        self.plan = plan
        self.c = estilo(plan)
        pj = os.path.join(voz_dir, "palabras.json")
        if not os.path.exists(pj):
            sys.exit(f"No encuentro {pj}. Primero alinea la voz con scripts/alinear.py (o usa --sin-voz).")
        self.voz = cargar_json(pj)
        self.voz_dir = voz_dir
        frases = list(plan.get("frases", []))
        if final == "tiktok":
            if "final_tiktok" not in plan:
                sys.exit("Para --final tiktok, añade \"final_tiktok\" en video.json (la última frase para TikTok).")
            frases[-1] = plan["final_tiktok"]
        nv = len(self.voz["frases"])
        if len(frases) != nv:
            sys.exit(f"video.json tiene {len(frases)} frases y la voz tiene {nv}. Tiene que haber un objeto en \"frases\" "
                     "por cada línea del guion (en el mismo orden).")
        # versión (a por defecto; b con --sufijo b): "versiones" en un elemento y "titular_b" en una frase
        self.version = version
        propias = []
        for f in frases:
            f = dict(f)
            if f"titular_{version}" in f:
                f["titular"] = f[f"titular_{version}"]
            f["elementos"] = [e for e in f.get("elementos", []) if version in e.get("versiones", [version])]
            propias.append(f)
        frases = propias
        self.frases = frases
        self.pal = self.voz["palabras"]
        for w in self.pal:
            w["n"] = normaliza(limpia(w["t"]))
        ult = self.voz["frases"][-1]["fin"]
        self.dur = max(self.voz.get("duracion") or 0, ult + 0.6)
        self.ini = [f["ini"] for f in self.voz["frases"]]
        self.ventana = []
        for i in range(nv):
            a = 0.0 if i == 0 else max(0.0, self.ini[i] - 0.15)
            if i == nv - 1 and i > 0:
                # la última frase empieza justo al acabar la anterior: así los dos finales comparten el cuerpo exacto
                a = self.voz["frases"][i - 1]["fin"] + 0.02
            b = self.dur if i == nv - 1 else max(a + 0.2, self.ini[i + 1] - 0.15)
            self.ventana.append((a, b))

    def ancla(self, i, valor, defecto=None):
        """Convierte 'palabra', 'palabra#2' o un número (segundos desde el inicio de la frase) en segundos."""
        a0 = self.ventana[i][0]
        if valor is None:
            return a0 if defecto is None else defecto
        if isinstance(valor, (int, float)):
            return self.ini[i] + float(valor)
        texto, _, num = str(valor).partition("#")
        n = normaliza(texto)
        veces = int(num) if num.isdigit() else 1
        ws = [w for w in self.pal if w["frase"] == i]
        if self.voz["frases"][i].get("subtitulo"):
            # versión con citas: también vale una palabra de lo que se oye en la cita
            ws = ws + [dict(w, n=normaliza(limpia(w["t"]))) for w in self.voz["frases"][i]["subtitulo"]]
        for prueba in (lambda w: w["n"] == n, lambda w: w["n"].startswith(n) and n):
            hall = [w for w in ws if prueba(w)]
            if len(hall) >= veces:
                return max(a0, hall[veces - 1]["ini"] - 0.12)
        aviso(f"Frase {i + 1}: no encuentro la palabra «{valor}» para colocar un elemento; lo pongo al empezar la frase.")
        return a0

    def subtitulos(self, i):
        f = self.voz["frases"][i]
        if f.get("subtitulo"):
            return [dict(w, n=normaliza(limpia(w["t"]))) for w in f["subtitulo"]]
        return [w for w in self.pal if w["frase"] == i]


# ------------------------------------------------------------------ medios
def ruta_medio(lin, tabla, clave):
    rutas = lin.plan.get(tabla, {})
    r = rutas.get(clave, clave)
    p = r if os.path.isabs(r) else os.path.join(lin.dir, r)
    if not os.path.exists(p):
        sys.exit(f"No encuentro «{clave}» ({p}). Revisa \"{tabla}\" en video.json.")
    return p


_cache_img = {}


def carga_imagen(lin, clave):
    p = ruta_medio(lin, "imagenes", clave)
    if p not in _cache_img:
        _cache_img[p] = cg.quita_fondo(Image.open(p))
    return _cache_img[p]


def lee_clip(ruta, desde, dur, w, h, velocidad=1.0):
    """Devuelve una lista de fotogramas RGB de tamaño w×h (recortados para llenar)."""
    total = duracion_media(ruta)
    desde = max(0.0, min(desde, max(0.0, total - 0.1)))
    largo = min(total - desde, dur * velocidad + 0.2)
    vf = f"setpts=PTS/{velocidad},fps={FPS},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
    raw = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{desde:.3f}", "-t", f"{largo:.3f}", "-i", ruta, "-an",
                          "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    n = len(raw) // (w * h * 3)
    if n == 0:
        sys.exit(f"No he podido leer fotogramas de {ruta}.")
    arr = np.frombuffer(raw[:n * w * h * 3], np.uint8).reshape(n, h, w, 3)
    return [Image.fromarray(a) for a in arr]


def miniatura_clip(ruta):
    raw = subprocess.run([FFMPEG, "-v", "error", "-ss", "0.5", "-i", ruta, "-frames:v", "1", "-vf", "scale=320:-2",
                          "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    import io
    try:
        return Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:  # noqa: BLE001
        return None


# ------------------------------------------------------------------ elementos
POS_AUTO = {1: [(540, 850)], 2: [(380, 740), (700, 1010)], 3: [(320, 690), (750, 800), (470, 1100)],
            4: [(300, 680), (780, 680), (300, 1050), (780, 1050)]}
ANCHO_DEF = {"clip": 700, "imagen": 520, "icono": 250, "etiqueta": 560, "sello": 0, "precio": 0, "nota": 380,
             "palabra": 980, "grande": 1000, "cuadricula": 960, "pasos": 860, "rasga": 520, "esquema": 600}


class Sprite:
    """Imagen RGBA ya girada y con sombra, más el punto que va en (x, y)."""

    def __init__(self, img, sombra=True, giro=0.0, sombra_d=(10, 12), c=None):
        img = cg.rota(img, giro)
        if sombra:
            img, _ = cg.con_sombra(img, *sombra_d, color=c["sombra"] if c else "#0E1B33")
        self.img = img
        self.cx, self.cy = img.width / 2 - sombra_d[0] / 2 * bool(sombra), img.height / 2 - sombra_d[1] / 2 * bool(sombra)


def transforma(img, escala=1.0, giro=0.0, alfa=1.0):
    if abs(escala - 1) > 0.01:
        img = img.resize((max(1, int(img.width * escala)), max(1, int(img.height * escala))), Image.BILINEAR)
    if abs(giro) > 0.05:
        img = img.rotate(giro, resample=Image.BILINEAR, expand=True)
    if alfa < 0.99:
        a = img.getchannel("A").point(lambda v: int(v * max(0, alfa)))
        img = img.copy(); img.putalpha(a)
    return img


def anim(tipo, t, te, tf):
    """Devuelve (escala, giro extra, dx, dy, alfa) para el instante t."""
    p = (t - te) / T_ENTRA
    esc, gir, dx, dy, alfa = 1.0, 0.0, 0.0, 0.0, 1.0
    if p < 1:
        if tipo == "pop":
            esc = 0.3 + 0.7 * rebote(p); alfa = suave(p * 3)
        elif tipo == "gira":
            esc = 0.35 + 0.65 * rebote(p); gir = -100 * (1 - suave(p)); alfa = suave(p * 3)
        elif tipo == "desliza":
            dx = -700 * (1 - suave(p)); gir = 8 * (1 - p)
        elif tipo == "desliza_d":
            dx = 700 * (1 - suave(p)); gir = -8 * (1 - p)
        elif tipo == "sello":
            q = min(1, (t - te) / 0.18)
            esc = 1.9 - 0.9 * suave(q); alfa = suave(q * 2)
            if q >= 1:
                dx = 5 * math.sin((t - te) * 90) * max(0, 1 - (t - te - 0.18) / 0.15)
        elif tipo == "cae":
            dy = -180 * (1 - suave(p)); gir = 10 * (1 - suave(p)); alfa = suave(p * 2.5)
        elif tipo == "sube":
            dy = 160 * (1 - suave(p)); alfa = suave(p * 2.5)
    q = (tf - t) / T_SALE
    if q < 1:
        alfa *= max(0, q); dy += 40 * (1 - q); esc *= 0.96 + 0.04 * q
    return esc, gir, dx, dy, alfa


class Elemento:
    def __init__(self, lin, i, d, k, n_auto, idx_auto):
        self.lin, self.i, self.d, self.k = lin, i, d, k
        self.c = lin.c
        self.tipo = d.get("tipo", "imagen")
        if self.tipo not in ANCHO_DEF and self.tipo != "tachar":
            sys.exit(f"Frase {i + 1}: el tipo de elemento «{self.tipo}» no existe. Tipos: {', '.join(list(ANCHO_DEF) + ['tachar'])}.")
        a, b = lin.ventana[i]
        sigue = int(d.get("sigue", 0))
        if sigue:
            b = lin.ventana[min(len(lin.ventana) - 1, i + sigue)][1]
        self.te = lin.ancla(i, d.get("en"))
        citas = lin.voz["frases"][i].get("citas") or []
        if d.get("con_cita") is not None and self.tipo == "clip" and citas:
            # versión con citas originales: el clip arranca justo cuando suena su audio (labios sincronizados)
            ci = citas[min(len(citas) - 1, int(d["con_cita"]) if not isinstance(d["con_cita"], bool) else 0)]
            self.te = max(lin.ventana[i][0], ci["t0"] - 0.05)
            d = dict(d, src=os.path.normpath(os.path.join(lin.voz_dir, ci["clip"])), desde=ci["desde"] - 0.05)
            self.d = d
        self.tf = lin.ancla(i, d["hasta"]) if "hasta" in d else b
        self.tf = max(self.tf, self.te + 0.4)
        if "x" in d and "y" in d:
            self.x, self.y = float(d["x"]), float(d["y"])
        else:
            pos = POS_AUTO.get(n_auto, POS_AUTO[4])[min(idx_auto, 3)]
            self.x, self.y = pos
        r = cg._rng(("giro", i, k))
        self.giro = float(d.get("giro", r.uniform(-5, 5)))
        self.ancho = int(d.get("ancho", ANCHO_DEF.get(self.tipo, 500) if n_auto <= 1 or self.tipo not in ("clip", "imagen")
                               else int(ANCHO_DEF[self.tipo] * 0.78)))
        defecto_entra = {"sello": "sello", "clip": "cae", "imagen": "gira", "icono": "pop", "palabra": "pop",
                         "precio": "pop", "rasga": "pop", "esquema": "cae", "etiqueta": "desliza"}.get(self.tipo, "pop")
        self.entra = d.get("entra", defecto_entra)
        self.sprite = None
        self.frames = None
        self.extra = {}

    # ---- construcción perezosa del sprite estático
    def construir(self):
        c, d, t = self.c, self.d, self.tipo
        if t == "imagen":
            img = carga_imagen(self.lin, d["src"])
            img = img.resize((self.ancho, int(img.height * self.ancho / img.width)), Image.LANCZOS)
            if d.get("pegatina", True):
                img = cg.pegatina(img, borde=10, color=c["papel"], contorno=c["texto"], grosor=2)
            self.sprite = Sprite(img, giro=self.giro, c=c)
        elif t == "icono":
            col = c.get(d["color"], d["color"]) if d.get("color") else None
            img = cg.pegatina(cg.icono(d["nombre"], self.ancho, c, col), borde=10, color=c["papel"], contorno=c["texto"], grosor=2)
            self.sprite = Sprite(img, giro=self.giro, c=c)
        elif t == "etiqueta":
            img = cg.etiqueta(d["texto"], c, tam=d.get("tam", 50), fondo=d.get("fondo", "papel"),
                              tinta=d.get("tinta", "texto" if d.get("fondo", "papel") in ("papel", "periodico") else "papel"),
                              semilla=(self.i, self.k), ancho_max=self.ancho)
            if d.get("cinta", True):
                img = con_cinta(img, (self.i, self.k))
            self.sprite = Sprite(img, giro=self.giro, c=c)
        elif t == "sello":
            col = c.get(d.get("color", "rojo"), d.get("color", "rojo"))
            self.sprite = Sprite(cg.sello(d["texto"], col, tam=d.get("tam", 84), semilla=(self.i, self.k)), sombra=False,
                                 giro=float(d.get("giro", -9)), c=c)
        elif t == "precio":
            self.sprite = Sprite(cg.precio(d["texto"], c, tam=d.get("tam", 58)), giro=self.giro, c=c)
        elif t == "nota":
            self.sprite = Sprite(con_cinta(cg.nota(d["texto"], c, tam=d.get("tam", 44), semilla=(self.i, self.k), ancho=self.ancho),
                                           (self.i, self.k)), giro=self.giro, c=c)
        elif t == "palabra":
            self.sprite = Sprite(cg.palabra_caja(d["texto"], c, tam=d.get("tam", 170), ancho_max=self.ancho),
                                 giro=float(d.get("giro", -2)), c=c)
        elif t == "esquema":
            w, h = self.ancho, int(self.ancho * 0.72)
            p = cg.cuadriculado(w, h, c, (self.i, self.k))
            ic = cg.icono(d.get("icono", "estrella"), int(h * 0.62), c)
            cg.pega(p, ic, (w - ic.width) // 2 - (60 if d.get("texto") else 0), (h - ic.height) // 2)
            if d.get("texto"):
                f = fuente("cursiva", 40)
                ImageDraw.Draw(p).text((w - ancho_texto(d["texto"], f) - 30, h - 70), d["texto"], font=f, fill=hexrgb(c["texto"]))
            self.sprite = Sprite(con_cinta(p, (self.i, self.k)), giro=self.giro, c=c)
        elif t == "clip":
            self.construir_clip()
        elif t == "rasga":
            de = carga_imagen(self.lin, d["de"])
            de = de.resize((self.ancho, int(de.height * self.ancho / de.width)), Image.LANCZOS)
            de = cg.pegatina(de, borde=10, color=c["papel"], contorno=c["texto"], grosor=2)
            mask = cg.borde_rasgado(de.width // 2 + 18, de.height, ("rasga", self.i), amp=16, lados="e")
            izq = Image.new("RGBA", de.size, (0, 0, 0, 0)); izq.paste(de.crop((0, 0, de.width // 2 + 18, de.height)), (0, 0))
            a = Image.new("L", de.size, 0); a.paste(mask, (0, 0))
            izq.putalpha(Image.fromarray(np.minimum(np.array(izq.getchannel("A")), np.array(a))))
            der = de.copy()
            da = np.array(der.getchannel("A")); da[np.array(a) > 128] = 0
            der.putalpha(Image.fromarray(da))
            self.extra = {"entera": Sprite(de, giro=self.giro, c=c), "izq": Sprite(izq, giro=self.giro, c=c),
                          "der": Sprite(der, giro=self.giro, c=c), "t_rasga": self.lin.ancla(self.i, d.get("rasga_en", d.get("cuando")),
                                                                                             self.te + 0.8)}
            nueva = carga_imagen(self.lin, d["a"])
            aw = int(d.get("ancho_a", self.ancho))
            nueva = nueva.resize((aw, int(nueva.height * aw / nueva.width)), Image.LANCZOS)
            self.extra["nueva"] = Sprite(cg.pegatina(nueva, borde=10, color=c["papel"], contorno=c["texto"], grosor=2),
                                         giro=-self.giro * 0.6, c=c)
            self.sprite = self.extra["entera"]
        elif t in ("grande", "cuadricula", "pasos", "tachar"):
            self.sprite = None  # se dibujan por partes
            if t == "grande":
                self.preparar_grande()
            elif t == "cuadricula":
                self.preparar_cuadricula()
            elif t == "pasos":
                self.preparar_pasos()

    def construir_clip(self):
        d, c = self.d, self.c
        w = self.ancho - 44
        ruta = ruta_medio(self.lin, "clips", d["src"])
        prop = d.get("proporcion")
        if prop:
            h = int(w / float(prop))
        else:
            mini = miniatura_clip(ruta)
            h = int(w * (mini.height / mini.width)) if mini else int(w * 9 / 16)
            h = min(h, int(w * 1.25))
        pie = d.get("pie", self.lin.plan.get("fuente_clips"))
        marco, (mx, my) = cg.polaroid(w, h, pie or None, c, (self.i, self.k))
        cinta = None
        if d.get("cinta", True):
            # la cinta va en una capa aparte, por encima de la foto
            lienzo = Image.new("RGBA", (marco.width + 60, marco.height + 60), (0, 0, 0, 0))
            lienzo.alpha_composite(marco, (30, 30))
            cinta = con_cinta(Image.new("RGBA", marco.size, (0, 0, 0, 0)), (self.i, self.k))
            marco, mx, my = lienzo, mx + 30, my + 30
        self.extra = {"w": w, "h": h, "ruta": ruta,
                      "foto_dx": mx + w / 2 - marco.width / 2, "foto_dy": my + h / 2 - marco.height / 2}
        # el marco se gira una vez; la foto se gira aparte en cada fotograma
        self.sprite = Sprite(marco, giro=self.giro, c=c)
        if cinta is not None:
            self.extra["cinta"] = cinta.rotate(self.giro, resample=Image.BICUBIC, expand=True)

    def foto(self, t):
        d = self.d
        if self.frames is None:
            dur = self.tf - self.te + 0.5
            kb = 1.10
            w, h = self.extra["w"], self.extra["h"]
            self.frames = lee_clip(self.extra["ruta"], float(d.get("desde", 0)), dur, int(w * kb), int(h * kb),
                                   float(d.get("velocidad", 1.0)))
        idx = int((t - self.te) * FPS)
        if idx >= len(self.frames):
            idx = len(self.frames) - 1  # se queda en el último fotograma (el zoom sigue moviéndose)
        fr = self.frames[max(0, idx)]
        w, h = self.extra["w"], self.extra["h"]
        p = suave((t - self.te) / max(0.5, self.tf - self.te))
        z = 1.10 - 0.08 * p if self.k % 2 else 1.02 + 0.08 * p
        cw, ch = w * z / 1.10, h * z / 1.10
        cw, ch = min(fr.width, w * fr.width / (w * 1.10) * z), min(fr.height, h * fr.height / (h * 1.10) * z)
        x0 = (fr.width - cw) * (0.3 + 0.4 * p) if self.k % 2 == 0 else (fr.width - cw) * (0.7 - 0.4 * p)
        y0 = (fr.height - ch) / 2
        return fr.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((w, h), Image.BILINEAR).convert("RGBA")

    def preparar_grande(self):
        d, c = self.d, self.c
        palabras = d["texto"].split()
        tam = d.get("tam", 116)
        f = fuente("black", tam)
        while True:
            lineas, actual = [], []
            for p in palabras:
                prueba = actual + [p]
                if sum(ancho_texto(limpia(x), f) + 64 for x in prueba) > self.ancho and actual:
                    lineas.append(actual); actual = [p]
                else:
                    actual = prueba
            lineas.append(actual)
            if len(lineas) <= 3 or tam < 60:
                break
            tam -= 8; f = fuente("black", tam)
        piezas = []
        ws = [w for w in self.lin.pal if w["frase"] == self.i]
        j = 0
        t0 = self.te
        alto = tam * 1.45
        y = self.y - alto * len(lineas) / 2 + alto / 2
        k = 0
        for li in lineas:
            imgs = []
            for p in li:
                clave = p.startswith("**") or p.endswith("**")
                img = cg.recorte_texto(limpia(p), tam, c, 1 if clave else (k % 2) * 2, semilla=(self.i, k))
                imgs.append(img); k += 1
            total = sum(im.width for im in imgs) + 6 * (len(imgs) - 1)
            x = self.x - total / 2
            for p, im in zip(li, imgs):
                n = normaliza(limpia(p))
                t_ap = None
                for jj in range(j, len(ws)):
                    if ws[jj]["n"] == n:
                        t_ap = ws[jj]["ini"] - 0.1; j = jj + 1; break
                piezas.append({"img": cg.rota(im, cg._rng(("g", self.i, x)).uniform(-4, 4)), "x": x + im.width / 2, "y": y, "t": t_ap})
                x += im.width + 6
            y += alto
        # las que no se oyen se reparten
        sin = [p for p in piezas if p["t"] is None]
        if sin:
            for n_, p in enumerate(piezas):
                if p["t"] is None:
                    p["t"] = t0 + (self.tf - t0) * 0.7 * n_ / max(1, len(piezas))
        self.extra["piezas"] = piezas

    def preparar_cuadricula(self):
        d, c = self.d, self.c
        n = int(d.get("n", 24)); cols = int(d.get("columnas", 6))
        filas = math.ceil(n / cols)
        cw = int(self.ancho / cols) - 14
        chh = int(cw * 16 / 9)
        mini = None
        if d.get("src"):
            if d["src"] in self.lin.plan.get("clips", {}):
                mini = miniatura_clip(ruta_medio(self.lin, "clips", d["src"]))
            else:
                mini = carga_imagen(self.lin, d["src"]).convert("RGB")
        tarjeta, _ = cg.con_sombra(cg.tarjeta_reel(cw, chh, c, 1, mini), 5, 6, color=c["sombra"])
        total_h = filas * (chh + 14)
        if total_h > ZONA_CENTRO[3] - ZONA_CENTRO[1]:
            f = (ZONA_CENTRO[3] - ZONA_CENTRO[1] - 20) / total_h
            cw, chh = int(cw * f), int(chh * f)
            tarjeta, _ = cg.con_sombra(cg.tarjeta_reel(cw, chh, c, 1, mini), 5, 6, color=c["sombra"])
            total_h = filas * (chh + 14)
        t_lleno = self.lin.ancla(self.i, d["llena"]) if "llena" in d else self.te + min(1.6, (self.tf - self.te) * 0.6)
        celdas = []
        x0 = self.x - cols * (cw + 14) / 2 + (cw + 14) / 2
        y0 = self.y - total_h / 2 + (chh + 14) / 2
        orden = list(range(n))
        cg._rng(("orden", self.i)).shuffle(orden) if d.get("desordena", False) else None
        for k in range(n):
            fila, col = divmod(k, cols)
            celdas.append({"x": x0 + col * (cw + 14), "y": y0 + fila * (chh + 14),
                           "t": self.te + (t_lleno - self.te) * orden[k] / max(1, n - 1)})
        self.extra = {"tarjeta": tarjeta, "celdas": celdas}

    def preparar_pasos(self):
        d, c = self.d, self.c
        textos = d["textos"]
        ens = d.get("en_cada", [None] * len(textos))
        f = fuente("bold", d.get("tam", 50))
        cards = []
        for k, tx in enumerate(textos):
            et = cg.etiqueta(tx, c, tam=d.get("tam", 62), semilla=("paso", self.i, k), ancho_max=self.ancho - 160)
            lienzo = Image.new("RGBA", (et.width + 110, max(et.height, 110)), (0, 0, 0, 0))
            lienzo.alpha_composite(et, (90, (lienzo.height - et.height) // 2))
            circ = Image.new("RGBA", (110, 110), (0, 0, 0, 0))
            dd = ImageDraw.Draw(circ)
            dd.ellipse([4, 4, 106, 106], fill=hexrgb(c["acento"]), outline=hexrgb(c["texto"]), width=6)
            fn = fuente("black", 60)
            s = str(k + 1)
            x0, y0, x1, y1 = fn.getbbox(s)
            dd.text((55 - (x1 - x0) / 2 - x0, 55 - (y1 - y0) / 2 - y0), s, font=fn, fill=(255, 255, 255))
            lienzo.alpha_composite(circ, (0, (lienzo.height - 110) // 2))
            spr = Sprite(lienzo, giro=cg._rng(("pg", self.i, k)).uniform(-3, 3), c=c)
            t_k = self.lin.ancla(self.i, ens[k]) if k < len(ens) and ens[k] is not None else \
                self.te + k * min(0.9, (self.tf - self.te) / (len(textos) + 1))
            cards.append({"spr": spr, "t": t_k})
        alto = sum(cd["spr"].img.height for cd in cards) + 20 * (len(cards) - 1)
        y = self.y - alto / 2
        for cd in cards:
            cd["y"] = y + cd["spr"].img.height / 2
            y += cd["spr"].img.height + 20
        self.extra["cards"] = cards
        _ = f

    # ---- dibujo
    def dibuja(self, lienzo, t, elementos):
        if t < self.te or t >= self.tf:
            return
        if self.sprite is None and not self.extra:
            self.construir()
        tipo = self.tipo
        esc, gir, dx, dy, alfa = anim(self.entra, t, self.te, self.tf)
        # «respira»: flota unos píxeles para que nada se quede quieto del todo
        fase = self.k * 1.9 + self.i * 0.7
        dx += 3 * math.cos(t * 2.1 + fase)
        dy += 6 * math.sin(t * 2.6 + fase)
        if tipo == "clip":
            self.pega_sprite(lienzo, self.sprite, esc, gir, dx, dy, alfa, foto=self.foto(t))
        elif tipo == "rasga":
            tr = self.extra["t_rasga"]
            if t < tr:
                self.pega_sprite(lienzo, self.extra["entera"], esc, gir, dx, dy, alfa)
            else:
                q = suave((t - tr) / 0.45)
                if q < 1:
                    self.pega_sprite(lienzo, self.extra["izq"], 1, 12 * q, dx - 260 * q, dy + 60 * q, alfa * (1 - q))
                    self.pega_sprite(lienzo, self.extra["der"], 1, -12 * q, dx + 260 * q, dy + 60 * q, alfa * (1 - q))
                e2 = anim("pop", t, tr + 0.08, self.tf)
                if t >= tr + 0.08:
                    self.pega_sprite(lienzo, self.extra["nueva"], e2[0], e2[1], e2[2], e2[3], e2[4])
        elif tipo == "grande":
            for p in self.extra["piezas"]:
                if t >= p["t"]:
                    e = anim("pop", t, p["t"], self.tf)
                    im = transforma(p["img"], e[0], e[1], e[4])
                    cg.pega(lienzo, im, p["x"] - im.width / 2 + e[2], p["y"] - im.height / 2 + e[3] + 4 * math.sin(t * 2.4 + p["x"] * 0.01))
        elif tipo == "cuadricula":
            tj = self.extra["tarjeta"]
            for cel in self.extra["celdas"]:
                if t >= cel["t"]:
                    e = anim("pop", t, cel["t"], self.tf)
                    im = transforma(tj, e[0], 0, e[4])
                    cg.pega(lienzo, im, cel["x"] - im.width / 2, cel["y"] - im.height / 2 + e[3] + 4 * math.sin(t * 2.6 + cel["x"] * 0.02))
        elif tipo == "pasos":
            for cd in self.extra["cards"]:
                if t >= cd["t"]:
                    e = anim("desliza_d", t, cd["t"], self.tf)
                    self.pega_sprite(lienzo, cd["spr"], e[0], e[1], e[2] + dx, e[3] + dy, e[4], y=cd["y"])
        elif tipo == "tachar":
            caja = self.caja_objetivo(elementos)
            if caja:
                x0, y0, x1, y1 = caja
                prog = min(1.0, (t - self.te) / 0.45)
                im = cg.tachon(int(x1 - x0), int(y1 - y0), self.c.get(self.d.get("color", "rojo"), self.d.get("color", "rojo")),
                               prog, grosor=int(self.d.get("grosor", 24)), semilla=self.i)
                cg.pega(lienzo, im, x0, y0)
        else:
            self.pega_sprite(lienzo, self.sprite, esc, gir, dx, dy, alfa)

    def caja_objetivo(self, elementos):
        d = self.d
        if "sobre" in d:
            k = int(d["sobre"])
            hermanos = [e for e in elementos if e.i == self.i]
            if 0 <= k < len(hermanos) and hermanos[k] is not self:
                return hermanos[k].caja()
            aviso(f"Frase {self.i + 1}: \"sobre\": {k} no apunta a otro elemento de la frase.")
            return None
        w, h = int(d.get("ancho", 400)), int(d.get("alto", 300))
        return (self.x - w / 2, self.y - h / 2, self.x + w / 2, self.y + h / 2)

    def caja(self):
        if self.sprite is None and not self.extra:
            self.construir()
        s = self.sprite
        if s is None:
            return None
        return (self.x - s.cx, self.y - s.cy, self.x - s.cx + s.img.width, self.y - s.cy + s.img.height)

    def pega_sprite(self, lienzo, spr, esc, gir, dx, dy, alfa, foto=None, y=None):
        y = self.y if y is None else y
        img = spr.img
        if foto is not None:
            img = img.copy()
            fr = foto.rotate(self.giro, resample=Image.BILINEAR, expand=True)
            a = math.radians(self.giro)
            fx, fy = self.extra["foto_dx"], self.extra["foto_dy"]
            rx = fx * math.cos(a) + fy * math.sin(a)
            ry = -fx * math.sin(a) + fy * math.cos(a)
            cx, cy = spr.cx, spr.cy
            img.alpha_composite(fr, (int(cx + rx - fr.width / 2), int(cy + ry - fr.height / 2)))
            ci = self.extra.get("cinta")
            if ci is not None:
                img.alpha_composite(ci, (int(cx - ci.width / 2), int(cy - ci.height / 2)))
        cx, cy = spr.cx, spr.cy
        if esc != 1 or abs(gir) > 0.05 or alfa < 0.99:
            w0, h0 = img.size
            img = transforma(img, esc, gir, alfa)
            cx = cx * esc + (img.width - w0 * esc) / 2
            cy = cy * esc + (img.height - h0 * esc) / 2
        cg.pega(lienzo, img, self.x - cx + dx, y - cy + dy)


def con_cinta(img, semilla):
    r = cg._rng(("cinta", semilla))
    w, h = img.size
    out = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    out.alpha_composite(img, (30, 30))
    t = cg.cinta(int(min(170, max(90, w * 0.32))), 42, semilla).rotate(r.uniform(-12, 12), expand=True)
    out.alpha_composite(t, (int(30 + w / 2 - t.width / 2 + r.uniform(-w * 0.2, w * 0.2)), max(0, 30 - t.height // 2)))
    return out


# ------------------------------------------------------------------ titular
class Titular:
    def __init__(self, lin):
        self.lin = lin
        self.bloques = []  # (t_ini, t_fin, piezas)
        actual = None
        for i, f in enumerate(lin.frases):
            tit = f.get("titular")
            if tit is None:
                continue
            if isinstance(tit, (str, dict)):
                tit = [tit]
            lineas = []
            for ln in tit:
                if isinstance(ln, dict):
                    texto, en = ln["texto"], ln.get("en")
                else:
                    texto, _, en = ln.partition("@")
                    en = en or None
                if not lineas and en:
                    aviso(f"Frase {i + 1}: la primera línea del titular lleva @ y el titular se queda vacío hasta esa palabra. "
                          "Quita la @ de la primera línea.")
                lineas.append((texto.strip(), lin.ancla(i, en)))
            if actual:
                actual["fin"] = lin.ventana[i][0]
            actual = {"ini": lin.ventana[i][0], "fin": lin.dur, "lineas": lineas, "i": i}
            self.bloques.append(actual)
        for b in self.bloques:
            self.prepara(b)

    def prepara(self, b):
        c = self.lin.c
        n = len(b["lineas"])
        tam = 124 if n <= 2 else 100
        while True:
            filas = []
            for texto, _ in b["lineas"]:
                filas.append([(limpia(p), p.startswith("**") or p.endswith("**")) for p in texto.split()])
            anchos = [sum(ancho_texto(p, fuente("black", tam)) + 50 for p, _ in fila) for fila in filas]
            if max(anchos + [0]) <= 1010 or tam <= 64:
                break
            tam -= 6
        if tam <= 64:
            aviso(f"Frase {b['i'] + 1}: el titular es muy largo; usa 2–4 palabras por línea.")
        alto = tam * 1.38
        y0 = 290 - alto * (n - 1) / 2
        piezas = []
        k = 0
        for li, (fila, (_, t_l)) in enumerate(zip(filas, b["lineas"])):
            imgs = []
            for j, (p, clave) in enumerate(fila):
                var = 1 if clave else [0, 2, 3, 0, 4][(k + li) % 5]
                im = cg.recorte_texto(p, tam, c, var, semilla=(b["i"], li, j), pad=(20, 9))
                imgs.append(im); k += 1
            total = sum(im.width for im in imgs) - 8 * (len(imgs) - 1)
            x = 540 - total / 2
            for j, im in enumerate(imgs):
                r = cg._rng(("tit", b["i"], li, j))
                sp, _ = cg.con_sombra(im, 6, 7, color=c["sombra"], alfa=0.28)
                piezas.append({"img": sp, "x": x + im.width / 2, "y": y0 + li * alto + r.uniform(-6, 6),
                               "giro": r.uniform(-4, 4), "t": max(b["ini"], t_l) + j * 0.07, "fase": r.uniform(0, 6.28)})
                x += im.width - 8
        b["piezas"] = piezas

    def dibuja(self, lienzo, t):
        for b in self.bloques:
            if b["ini"] <= t < b["fin"]:
                for p in b["piezas"]:
                    if t < p["t"]:
                        continue
                    e = anim("pop", t, p["t"], b["fin"] + 1)
                    g = p["giro"] + 1.1 * math.sin(t * 3.4 + p["fase"])
                    im = transforma(p["img"], e[0] * (1 + 0.012 * math.sin(t * 2.7 + p["fase"])), g, e[4])
                    cg.pega(lienzo, im, p["x"] - im.width / 2, p["y"] - im.height / 2 + e[3] + 4 * math.sin(t * 2.3 + p["fase"]))


# ------------------------------------------------------------------ subtítulos
class Subtitulos:
    def __init__(self, lin):
        self.lin = lin
        self.trozos = []
        self.tam = int(lin.plan.get("subtitulos_tam", 76))
        self.f = fuente("black", self.tam)
        for i in range(len(lin.frases)):
            if lin.frases[i].get("subtitulos") is False:
                continue  # por ejemplo, cuando la frase ya sale en grande
            ws = lin.subtitulos(i)
            if not ws:
                continue
            claves = marca_claves([w["t"] for w in ws])
            items = [{"t": limpia(w["t"]), "ini": w["ini"], "clave": cl} for w, cl in zip(ws, claves)]
            grupos, actual, ancho = [], [], 0
            for it in items:
                wa = ancho_texto(it["t"], self.f) + 30
                if actual and (ancho + wa > 960 or len(actual) >= 4):
                    # una palabra de enlace no cierra la línea
                    while len(actual) > 1 and normaliza(actual[-1]["t"]) in ENLACE:
                        it_prev = actual.pop()
                        ancho -= ancho_texto(it_prev["t"], self.f) + 30
                        grupos.append(actual); actual = [it_prev]; ancho = ancho_texto(it_prev["t"], self.f) + 30
                        break
                    else:
                        grupos.append(actual); actual, ancho = [], 0
                actual.append(it); ancho += wa
            if actual:
                grupos.append(actual)
            fin_frase = lin.ventana[i][1]
            for g_i, g in enumerate(grupos):
                t0 = max(lin.ventana[i][0], g[0]["ini"] - SUB_ANTES)
                t1 = grupos[g_i + 1][0]["ini"] - SUB_ANTES if g_i + 1 < len(grupos) else fin_frase
                self.trozos.append({"t0": t0, "t1": max(t0 + 0.2, t1), "items": g})
        self._cache = {}

    def palabra_img(self, texto, clave):
        k = (texto, clave)
        if k not in self._cache:
            f = self.f
            x0, y0, x1, y1 = f.getbbox(texto)
            w, h = x1 - x0 + 24, int(self.tam * 1.32)
            img = Image.new("RGBA", (w + 10, h + 10), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            ty = (h - (y1 - y0)) / 2 - y0
            if clave:
                d.text((12 - x0, ty), texto, font=f, fill=(255, 255, 255))
            else:
                d.text((12 - x0 + 4, ty + 5), texto, font=f, fill=hexrgb(self.lin.c["texto"]), stroke_width=7,
                       stroke_fill=hexrgb(self.lin.c["texto"]))
                d.text((12 - x0, ty), texto, font=f, fill=(255, 255, 255), stroke_width=7, stroke_fill=hexrgb(self.lin.c["texto"]))
            self._cache[k] = img
        return self._cache[k]

    def dibuja(self, lienzo, t):
        for tr in self.trozos:
            if tr["t0"] <= t < tr["t1"]:
                items = tr["items"]
                imgs = [self.palabra_img(it["t"], it["clave"]) for it in items]
                total = sum(im.width - 10 for im in imgs)
                x = 540 - total / 2
                d = ImageDraw.Draw(lienzo)
                # cajas naranjas detrás de los grupos de palabras clave
                xs = []
                for it, im in zip(items, imgs):
                    xs.append(x); x += im.width - 10
                k = 0
                while k < len(items):
                    if items[k]["clave"] and t >= items[k]["ini"] - SUB_ANTES:
                        j = k
                        while j + 1 < len(items) and items[j + 1]["clave"] and t >= items[j + 1]["ini"] - SUB_ANTES:
                            j += 1
                        x0, x1 = xs[k] - 2, xs[j] + imgs[j].width - 6
                        h = int(self.tam * 1.32)
                        d.rectangle([x0 + 6, Y_SUB - h / 2 + 8, x1 + 6, Y_SUB + h / 2 + 8], fill=hexrgb(self.lin.c["texto"]))
                        d.rectangle([x0, Y_SUB - h / 2, x1, Y_SUB + h / 2], fill=hexrgb(self.lin.c["acento"]))
                        k = j + 1
                    else:
                        k += 1
                for it, im, xx in zip(items, imgs, xs):
                    if t >= it["ini"] - SUB_ANTES:
                        q = min(1, (t - it["ini"] + SUB_ANTES) / 0.12)
                        dy = 14 * (1 - q)
                        cg.pega(lienzo, im, xx, Y_SUB - im.height / 2 + 5 + dy)
                return


def marca_claves(palabras):
    """Marca las palabras que van entre ** (aunque el grupo tenga varias palabras)."""
    out, dentro = [], False
    for p in palabras:
        empieza = p.startswith("**")
        termina = p.rstrip(".,;:!?…»\"'").endswith("**") and (len(p.strip("*.,;:!?…")) > 0)
        clave = dentro or empieza
        if empieza and termina and p.count("**") >= 2:
            out.append(True); continue
        if empieza:
            dentro = True
        if termina and dentro:
            out.append(True); dentro = False; continue
        out.append(clave)
    return out


# ------------------------------------------------------------------ personaje y tira
class Personaje:
    def __init__(self, lin):
        self.lin = lin
        cfg = lin.plan.get("personaje")
        self.activo = bool(cfg)
        if not self.activo:
            return
        carpeta = cfg["carpeta"] if os.path.isabs(cfg["carpeta"]) else os.path.join(lin.dir, cfg["carpeta"])
        if not os.path.isdir(carpeta):
            sys.exit(f"No encuentro la carpeta del personaje {carpeta}.")
        self.alto = int(cfg.get("alto", 470))
        self.x = int(cfg.get("x", 205))
        self.poses = {}
        for f in sorted(os.listdir(carpeta)):
            if f.lower().endswith((".png", ".webp")):
                img = cg.quita_fondo(Image.open(os.path.join(carpeta, f)))
                bb = img.getbbox()
                img = img.crop(bb) if bb else img
                img = img.resize((int(img.width * self.alto / img.height), self.alto), Image.LANCZOS)
                img = cg.pegatina(img, borde=7, color=lin.c["papel"], contorno=lin.c["texto"], grosor=2)
                self.poses[os.path.splitext(f)[0]] = img
        if not self.poses:
            sys.exit(f"No hay imágenes PNG en {carpeta}.")
        defecto = cfg.get("pose", sorted(self.poses)[0])
        self.cambios = []  # (t, pose)
        pose = defecto
        for i, fr in enumerate(lin.frases):
            if fr.get("pose"):
                pose = fr["pose"]
            self.cambios.append((lin.ventana[i][0], pose))
            for extra in fr.get("poses", []):
                self.cambios.append((lin.ancla(i, extra.get("en")), extra["pose"]))
        self.cambios.sort(key=lambda x: x[0])
        for _, p in self.cambios:
            if p not in self.poses:
                aviso(f"La pose «{p}» no está en {carpeta} (hay: {', '.join(sorted(self.poses))}).")
        halo = cg.papel(400, 400, lin.c["acento"], semilla="halo", rasgado=False, textura=4)
        m = Image.new("L", (400 * 2, 400 * 2), 0)
        ImageDraw.Draw(m).ellipse([0, 0, 800, 800], fill=255)
        m = m.resize((400, 400), Image.LANCZOS)
        halo.putalpha(m)
        self.halo = halo

    def pose_en(self, t):
        pose, t_cambio = self.cambios[0][1], 0.0
        for tc, p in self.cambios:
            if tc <= t:
                pose, t_cambio = p, tc
        return self.poses.get(pose, next(iter(self.poses.values()))), t_cambio

    def dibuja(self, lienzo, t):
        if not self.activo:
            return
        img, tc = self.pose_en(t)
        base_y = H - 30
        hx, hy = self.x, base_y - self.alto * 0.62
        esc_h = 1 + 0.04 * math.sin(t * 2.2)
        h2 = transforma(self.halo, esc_h, t * 12 % 360)
        cg.pega(lienzo, h2, hx - h2.width / 2, hy - h2.height / 2)
        q = suave((t - tc) / 0.22) if t - tc < 0.22 else 1.0
        resp = 3 * math.sin(t * 2 * math.pi / 2.6)
        bal = 0.4 * math.sin(t * 2 * math.pi / 3.7)
        im = transforma(img, 0.94 + 0.06 * q, bal)
        cg.pega(lienzo, im, self.x - im.width / 2, base_y - im.height + resp + 8 * (1 - q))


class Tira:
    def __init__(self, lin):
        self.activo = lin.plan.get("tira", True)
        if not self.activo:
            return
        minis = []
        for clave in lin.plan.get("clips", {}):
            m = miniatura_clip(ruta_medio(lin, "clips", clave))
            if m:
                minis.append(m)
        self.alto = 190
        self.img = cg.tira_pelicula(minis, self.alto, lin.c).convert("RGBA")
        self.img, _ = cg.con_sombra(self.img, 0, 10, color=lin.c["sombra"], alfa=0.3)
        self.y = 1555

    def dibuja(self, lienzo, t):
        if not self.activo:
            return
        x = -int((t * 70) % (self.img.width - W - 10))
        trozo = self.img.crop((-x, 0, -x + W, self.img.height))
        trozo = trozo.rotate(-1.5, resample=Image.BILINEAR, expand=True)
        cg.pega(lienzo, trozo, (W - trozo.width) / 2, self.y)


class Transiciones:
    def __init__(self, lin):
        self.lin = lin
        n = len(lin.frases)
        # en la última frase la transición empieza justo en el corte, para no tocar el cuerpo compartido
        self.ts = [lin.ventana[i][0] + (0.12 if i == n - 1 else 0.0) for i, f in enumerate(lin.frases) if f.get("transicion") and i > 0]
        self.hoja = None

    def dibuja(self, lienzo, t):
        for t0 in self.ts:
            if t0 - 0.12 <= t < t0 + 0.28:
                if self.hoja is None:
                    self.hoja = cg.papel(1400, 1150, self.lin.c["acento"], semilla="trans", amp=26).rotate(-8, expand=True)
                p = (t - (t0 - 0.12)) / 0.4
                y = -1500 + 3600 * suave(p)
                cg.pega(lienzo, self.hoja, (W - self.hoja.width) / 2, y)


# ------------------------------------------------------------------ escena completa
class Escena:
    def __init__(self, lin, rapido=False):
        self.lin = lin
        self.fondo = cg.fondo(lin.c, semilla=lin.plan.get("semilla", 1), decorado=lin.plan.get("decorado", True))
        self.elementos = []
        for i, f in enumerate(lin.frases):
            els = f.get("elementos", [])
            auto = [d for d in els if not ("x" in d and "y" in d) and d.get("tipo") != "tachar"]
            for k, d in enumerate(els):
                idx = auto.index(d) if d in auto else 0
                self.elementos.append(Elemento(lin, i, d, k, len(auto), idx))
        self.titular = Titular(lin)
        self.subs = Subtitulos(lin) if lin.plan.get("subtitulos", True) else None
        self.pers = Personaje(lin)
        self.tira = Tira(lin)
        self.trans = Transiciones(lin)
        self.rapido = rapido

    def fotograma(self, t):
        img = self.fondo.copy()
        self.tira.dibuja(img, t)
        for e in self.elementos:
            e.dibuja(img, t, self.elementos)
            if e.frames is not None and t >= e.tf:
                e.frames = None  # libera memoria
        self.titular.dibuja(img, t)
        self.pers.dibuja(img, t)
        if self.subs:
            self.subs.dibuja(img, t)
        self.trans.dibuja(img, t)
        return img

    def huecos_quietos(self, maximo=0.6):
        """Estima desde el plan los tramos sin nada en el centro o sin titular (antes de montar nada)."""
        paso = 0.1
        n = int(self.lin.dur / paso)
        centro, titular = [], []
        for k in range(n):
            t = k * paso
            centro.append(any(e.te <= t < e.tf and e.tipo != "tachar" for e in self.elementos))
            titular.append(any(b["ini"] <= t < b["fin"] and any(p["t"] <= t for p in b.get("piezas", []))
                               for b in self.titular.bloques))
        for nombre, serie in (("centro", centro), ("titular", titular)):
            k = 0
            while k < n:
                if not serie[k]:
                    j = k
                    while j < n and not serie[j]:
                        j += 1
                    if (j - k) * paso > maximo + 0.05:
                        aviso(f"Ritmo: zona {nombre} vacía {(j - k) * paso:.1f} s desde el segundo {k * paso:.1f}; "
                              "añade un elemento con \"en\" (o una línea de titular) ahí.")
                    k = j
                else:
                    k += 1

    def revisar(self):
        """Avisos automáticos sobre el estado final de cada frase."""
        self.huecos_quietos()
        for i in range(len(self.lin.frases)):
            cajas = []
            for e in self.elementos:
                if e.i != i or e.tipo in ("tachar", "grande", "cuadricula", "pasos"):
                    continue
                cj = e.caja()
                if not cj:
                    continue
                x0, y0, x1, y1 = cj
                if x0 < -30 or x1 > W + 30:
                    aviso(f"Frase {i + 1}: un elemento ({e.tipo}) se sale por los lados; muévelo o hazlo más pequeño.")
                if y0 < ZONA_CENTRO[1] - 70 or y1 > ZONA_CENTRO[3] + 60:
                    aviso(f"Frase {i + 1}: un elemento ({e.tipo}) invade el titular o los subtítulos (y={int(y0)}–{int(y1)}); "
                          f"la zona central va de y={ZONA_CENTRO[1]} a {ZONA_CENTRO[3]}.")
                for cj2, t2, e2 in cajas:
                    if e2.tf <= e.te or e.tf <= e2.te:
                        continue  # no están a la vez en pantalla
                    ix = max(0, min(x1, cj2[2]) - max(x0, cj2[0])); iy = max(0, min(y1, cj2[3]) - max(y0, cj2[1]))
                    menor = min((x1 - x0) * (y1 - y0), (cj2[2] - cj2[0]) * (cj2[3] - cj2[1]))
                    if menor > 0 and ix * iy / menor > 0.55 and e.tipo != "sello" and t2 != "sello":
                        aviso(f"Frase {i + 1}: dos elementos ({t2} y {e.tipo}) se pisan mucho; sepáralos con x/y.")
                cajas.append((cj, e.tipo, e))


# ------------------------------------------------------------------ salida
def firma(lin, hasta):
    datos = {"plan": {k: v for k, v in lin.plan.items() if k not in ("final_tiktok", "portada", "frases", "voz", "voz_tiktok")},
             "frases": lin.frases[:-1], "pal": [w for w in lin.pal if w["ini"] < hasta],
             "subs": [f.get("subtitulo") for f in lin.voz["frases"][:-1]],
             "hasta": hasta, "v": 3}
    for tabla in ("clips", "imagenes"):
        for clave in lin.plan.get(tabla, {}):
            p = ruta_medio(lin, tabla, clave)
            datos.setdefault("mtimes", []).append(os.path.getmtime(p))
    return hashlib.sha256(json.dumps(datos, sort_keys=True, default=str).encode()).hexdigest()[:16]


def codifica(escena, t0, t1, salida, rapido=False, etiqueta=""):
    n0, n1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    w, h = (W // 2, H // 2) if rapido else (W, H)
    cmd = [FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18" if not rapido else "26", "-pix_fmt", "yuv420p",
           "-r", str(FPS), salida]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t_ini = time.time()
    for n in range(n0, n1):
        img = escena.fotograma(n / FPS)
        if rapido:
            img = img.resize((w, h), Image.BILINEAR)
        pr.stdin.write(img.tobytes())
        if (n - n0) % (FPS * 10) == 0 and n > n0:
            v = (n - n0) / (time.time() - t_ini)
            print(f"  {etiqueta}{n / FPS:5.1f} s de {t1:.1f} · {v:.0f} fotogramas/s", flush=True)
    pr.stdin.close()
    if pr.wait():
        sys.exit("ffmpeg falló al codificar el vídeo.")


def pista_audio(lin, escena, salida):
    from sonidos import pista
    voz = os.path.join(lin.voz_dir, "voz_final.wav")
    n = int(lin.dur * 48000)
    mezcla = np.zeros(n, np.float32)
    if os.path.exists(voz):
        raw = subprocess.run([FFMPEG, "-v", "error", "-i", voz, "-ac", "1", "-ar", "48000", "-f", "f32le", "-"],
                             capture_output=True).stdout
        a = np.frombuffer(raw, np.float32)[:n]
        mezcla[:len(a)] += a
    if lin.plan.get("efectos", True):
        ev = []
        for e in escena.elementos:
            son = e.d.get("sonido", {"sello": "golpe", "tachar": "tachar", "palabra": "exito"}.get(e.tipo))
            if son:
                ev.append((e.te + (0.15 if e.tipo == "sello" else 0.0), son))
        for t0 in escena.trans.ts:
            ev.append((t0 - 0.05, "pasa"))
        if ev:
            p = pista(ev, lin.dur, ganancia=float(lin.plan.get("volumen_efectos", 0.35)))
            mezcla[:len(p)] += p[:n]
    import wave
    import alinear as al
    tmp = salida + ".mezcla.wav"
    with wave.open(tmp, "wb") as wv:
        wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(48000)
        wv.writeframes((np.clip(mezcla, -1, 1) * 32767).astype(np.int16).tobytes())
    if mezcla.any():
        al.normalizar(tmp, salida)  # el vídeo final, a −14 LUFS
        os.remove(tmp)
    else:
        os.replace(tmp, salida)


def hoja_muestras(escena, lin, carpeta):
    tiempos = []
    for i in range(len(lin.frases)):
        a, b = lin.ventana[i]
        t = max(a + 0.3, b - T_SALE - 0.15)  # al final de la frase: ya ha entrado todo
        tiempos.append((i, t))
    rutas = []
    por_hoja = 12
    for h0 in range(0, len(tiempos), por_hoja):
        lote = tiempos[h0:h0 + por_hoja]
        cols = 4
        tw, th = 240, 427
        filas = math.ceil(len(lote) / cols)
        hoja = Image.new("RGB", (cols * (tw + 10) + 10, filas * (th + 44) + 10), (40, 40, 40))
        d = ImageDraw.Draw(hoja)
        for k, (i, t) in enumerate(lote):
            img = escena.fotograma(t).resize((tw, th), Image.BILINEAR)
            x, y = 10 + (k % cols) * (tw + 10), 10 + (k // cols) * (th + 44)
            hoja.paste(img, (x, y))
            d.text((x + 4, y + th + 6), f"Frase {i + 1} · {t:.1f} s", font=fuente("bold", 22), fill=(240, 240, 240))
        ruta = os.path.join(carpeta, f"muestras_{h0 // por_hoja + 1}.png")
        hoja.save(ruta)
        rutas.append(ruta)
    return rutas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--muestras", action="store_true")
    ap.add_argument("--en", type=float, help="saca un fotograma en ese segundo")
    ap.add_argument("--final", default="instagram", choices=["instagram", "tiktok"])
    ap.add_argument("--voz", help="carpeta de la voz (por defecto, la de video.json; con --final tiktok, voz_tiktok)")
    ap.add_argument("--sufijo", default="", help="se añade al nombre del vídeo (por ejemplo, b)")
    ap.add_argument("--rapido", action="store_true", help="borrador a media resolución")
    ap.add_argument("--rehacer", action="store_true", help="no reutiliza el cuerpo guardado")
    a = ap.parse_args()
    plan_dir = os.path.dirname(os.path.abspath(a.plan))
    plan = cargar_json(a.plan)
    voz_rel = a.voz or (plan.get("voz_tiktok", "voz_tiktok") if a.final == "tiktok" else plan.get("voz", "voz"))
    voz_dir = voz_rel if os.path.isabs(voz_rel) else os.path.join(plan_dir, voz_rel)
    if a.final == "tiktok" and not os.path.exists(os.path.join(voz_dir, "palabras.json")):
        sys.exit(f"No encuentro {voz_dir}/palabras.json. Prepara la voz del final de TikTok con scripts/finales.py.")
    lin = Linea(plan_dir, plan, voz_dir, a.final, (a.sufijo or "a").lower())
    salida_dir = os.path.join(plan_dir, "salida")
    os.makedirs(salida_dir, exist_ok=True)
    escena = Escena(lin, a.rapido)
    escena.revisar()

    if a.en is not None:
        ruta = os.path.join(salida_dir, f"fotograma{('_' + a.sufijo) if a.sufijo else ''}_{a.en:06.2f}.png")
        escena.fotograma(a.en).save(ruta)
        print("Fotograma:", ruta)
    elif a.muestras:
        for r in hoja_muestras(escena, lin, salida_dir):
            print("Muestras:", r)
    else:
        nombre = plan.get("nombre") or os.path.basename(plan_dir)
        suf = (f"_{a.sufijo}" if a.sufijo else "") + ("_borrador" if a.rapido else "")
        final_mp4 = os.path.join(salida_dir, f"{nombre}{suf}_{a.final}.mp4")
        t_corte = int(lin.ventana[-1][0] * FPS) / FPS
        clave = firma(lin, t_corte) + ("r" if a.rapido else "")
        partes_dir = os.path.join(salida_dir, "partes")
        os.makedirs(partes_dir, exist_ok=True)
        # el cuerpo se hace por tandas de unos 20 s: si algo corta el proceso, al repetir el comando sigue donde iba
        cortes = [0.0]
        while cortes[-1] < t_corte - 0.01:
            cortes.append(min(t_corte, cortes[-1] + 20.0))
        piezas = []
        t_i = time.time()
        for k in range(len(cortes) - 1):
            t0, t1 = cortes[k], cortes[k + 1]
            ruta = os.path.join(partes_dir, f"cuerpo{suf}_{k:02d}.mp4")
            fir = f"{clave}:{t0:.3f}:{t1:.3f}"
            if not a.rehacer and os.path.exists(ruta) and os.path.exists(ruta + ".firma") and open(ruta + ".firma").read() == fir:
                print(f"  tanda {k + 1}/{len(cortes) - 1} ({t0:.0f}–{t1:.0f} s): ya hecha, la reutilizo")
            else:
                print(f"  tanda {k + 1}/{len(cortes) - 1} ({t0:.0f}–{t1:.0f} s)", flush=True)
                tmp = ruta + ".tmp.mp4"
                codifica(escena, t0, t1, tmp, a.rapido, "")
                os.replace(tmp, ruta)
                with open(ruta + ".firma", "w") as fh:
                    fh.write(fir)
            piezas.append(ruta)
        fin_mp4 = os.path.join(salida_dir, f"_final_{a.final}{suf}.mp4")
        print(f"Final ({a.final}): {t_corte:.1f}–{lin.dur:.1f} s")
        codifica(escena, t_corte, lin.dur, fin_mp4, a.rapido, "final ")
        lista = os.path.join(salida_dir, "_lista.txt")
        with open(lista, "w") as fh:
            for pz in piezas + [fin_mp4]:
                fh.write(f"file '{os.path.abspath(pz)}'\n")
        wav = os.path.join(salida_dir, f"_audio_{a.final}{suf}.wav")
        pista_audio(lin, escena, wav)
        r = subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-i", wav,
                            "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                            "-movflags", "+faststart", final_mp4], capture_output=True, text=True)
        if r.returncode:
            sys.exit("ffmpeg falló al unir: " + r.stderr[-500:])
        for f in (fin_mp4, lista, wav):
            os.remove(f)
        print(f"Vídeo: {final_mp4} ({lin.dur:.1f} s, {time.time() - t_i:.0f} s de render)")
        # control de ritmo real, por zonas, sobre el vídeo terminado
        r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ritmo.py"),
                            final_mp4, "--por-zona"], capture_output=True, text=True)
        lineas = (r.stdout or "").strip().splitlines()
        malos = [l for l in lineas if "quieto →" in l]
        if malos:
            aviso(f"Ritmo del vídeo: {len(malos)} tramo(s) quietos más de 0,6 s (detalle: ritmo.py {os.path.basename(final_mp4)} --por-zona). "
                  "Primero: " + malos[0].strip())
    if AVISOS:
        print(f"AVISOS ({len(AVISOS)}):")
        for m in AVISOS:
            print("  -", m)
    else:
        print("Sin avisos.")


if __name__ == "__main__":
    main()
