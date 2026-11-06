"""Utilidades comunes de collage-historia: rutas, colores, fuentes, texto y JSON."""
import json, os, re, shutil, sys, unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTES = os.path.join(RAIZ, "fuentes")
W, H, FPS = 1080, 1920, 30


def _ffmpeg():
    f = shutil.which("ffmpeg")
    if f:
        return f
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # noqa: BLE001
        return "ffmpeg"


FFMPEG = _ffmpeg()
FFPROBE = shutil.which("ffprobe")

# Estilos: el usuario puede cambiar cualquier color con "colores" en video.json.
ESTILOS = {
    "arena": {"fondo": "#EBDDC6", "acento": "#FF7A1A", "texto": "#0E1B33", "papel": "#FBF7EE",
              "rojo": "#D9412B", "periodico": "#E4E0D6", "sombra": "#0E1B33"},
    "noche": {"fondo": "#16213A", "acento": "#FF7A1A", "texto": "#0E1B33", "papel": "#FBF7EE",
              "rojo": "#E04A33", "periodico": "#D9D4C7", "sombra": "#000000"},
    "rosa": {"fondo": "#F3D9D3", "acento": "#E8505B", "texto": "#1E1B2E", "papel": "#FFFBF5",
             "rojo": "#C8323C", "periodico": "#E8E2D8", "sombra": "#1E1B2E"},
}

ARCHIVOS_FUENTE = {"black": "Poppins-Black.ttf", "bold": "Poppins-Bold.ttf", "semi": "Poppins-SemiBold.ttf",
                   "cursiva": "Lora-Italic.ttf"}
_cache_fuentes = {}

# Palabras de enlace: nunca cierran una línea de subtítulos.
ENLACE = set("""a al ante bajo con contra de del desde el en entre hacia hasta la las le lo los mi mis me nos o
para pero por que se si sin sobre su sus te tu tus u un una unas unos y ya ni e the of to and or for""".split())


def hexrgb(c, alfa=None):
    if isinstance(c, (tuple, list)):
        t = tuple(int(v) for v in c)
    else:
        c = c.lstrip("#")
        t = tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    return t + (alfa,) if alfa is not None else t


def estilo(plan):
    base = dict(ESTILOS.get(plan.get("estilo", "arena"), ESTILOS["arena"]))
    base.update(plan.get("colores", {}))
    return base


def fuente(nombre, tam):
    from PIL import ImageFont
    clave = (nombre, int(tam))
    if clave not in _cache_fuentes:
        ruta = os.path.join(FUENTES, ARCHIVOS_FUENTE.get(nombre, nombre))
        if not os.path.exists(ruta):
            sys.exit(f"Falta la fuente {ruta}. Vuelve a copiar la skill entera.")
        _cache_fuentes[clave] = ImageFont.truetype(ruta, int(tam))
    return _cache_fuentes[clave]


def normaliza(palabra):
    s = unicodedata.normalize("NFD", palabra.lower())
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", s)


def limpia(palabra):
    """Quita las marcas ** de una palabra del guion."""
    return palabra.replace("**", "")


def cargar_json(ruta):
    try:
        with open(ruta, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        sys.exit(f"No encuentro {ruta}.")
    except json.JSONDecodeError as e:
        sys.exit(f"{ruta} no es un JSON válido (línea {e.lineno}, columna {e.colno}): {e.msg}")


def guardar_json(ruta, datos):
    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(datos, fh, ensure_ascii=False, indent=1)


def ancho_texto(texto, f):
    if not texto:
        return 0
    x0, _, x1, _ = f.getbbox(texto)
    return x1 - x0


def parte_lineas(texto, f, ancho_max):
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if ancho_texto(prueba, f) <= ancho_max or not actual:
            actual = prueba
        else:
            lineas.append(actual); actual = p
    if actual:
        lineas.append(actual)
    return lineas


def suave(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def rebote(t):
    """Entrada con un pequeño pasado de largo (0 → 1, pasa a 1,08 y vuelve)."""
    t = max(0.0, min(1.0, t))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def duracion_media(ruta):
    import subprocess
    if FFPROBE:
        r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ruta],
                           capture_output=True, text=True)
        try:
            return float(r.stdout.strip())
        except ValueError:
            pass
    r = subprocess.run([FFMPEG, "-i", ruta], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    if not m:
        sys.exit(f"No puedo leer la duración de {ruta}.")
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
