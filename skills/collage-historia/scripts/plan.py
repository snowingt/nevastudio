#!/usr/bin/env python3
"""Borrador de video.json a partir del guion y del material que haya en la carpeta del proyecto.

Uso:  python3 scripts/plan.py P [--palabra HISTORIA] [--fuente "Película (Estudio, año)"]

Lee P/guion.txt y mira qué hay en P/clips/ (vídeos), P/imagenes/ (PNG) y P/personaje/ (poses PNG).
Escribe P/video.json con una frase por línea del guion: titular con las palabras en **negrita**, un clip o una imagen
por frase y la palabra final en grande. Es un punto de partida que funciona: luego se mejora a mano
(sellos, etiquetas, iconos, citas…) siguiendo referencias/plan.md. No sobrescribe un video.json que ya exista.
"""
import argparse, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import guardar_json, limpia, normaliza, ENLACE  # noqa: E402


def negritas(linea):
    return [m.strip() for m in re.findall(r"\*\*(.+?)\*\*", linea)]


def titular(linea):
    grupos = negritas(linea)
    if grupos:
        partes = [g.upper().strip(".,;:!?…¿¡") for g in grupos[:2]]
    else:
        # sin negritas: las primeras palabras de la frase, en orden (se leen como una frase, no al azar)
        palabras = [limpia(p).strip(".,;:!?…¿¡") for p in re.sub(r"\[[^\]]*\]", "", linea).split()]
        partes = [" ".join(palabras[:3]).upper()]
    salida = []
    for k, p in enumerate(partes):
        pal = p.split()[:3]
        while len(pal) > 1 and normaliza(pal[-1]) in ENLACE:
            pal.pop()  # un titular no acaba en «al», «de», «la»…
        p = " ".join(pal)
        ancla = max(pal, key=lambda x: len(normaliza(x)))  # la palabra más larga: no se confunde con otra
        salida.append(p if k == 0 else f"{p}@{normaliza(ancla)}")
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto")
    ap.add_argument("--palabra", help="palabra para comentar (si no, la busca tras «Comenta» en la última frase)")
    ap.add_argument("--fuente", help="pie de foto de los clips: título y año de la obra, p. ej. \"La liebre y la tortuga (2026)\"")
    ap.add_argument("--dos-finales", action="store_true", help="añade final_tiktok («Sígueme y escríbeme PALABRA por privado»)")
    ap.add_argument("--forzar", action="store_true", help="sobrescribe video.json si ya existe")
    a = ap.parse_args()
    P = a.proyecto
    destino = os.path.join(P, "video.json")
    if os.path.exists(destino) and not a.forzar:
        sys.exit(f"{destino} ya existe. Edítalo a mano o usa --forzar para empezar de cero.")
    with open(os.path.join(P, "guion.txt"), encoding="utf-8") as fh:
        lineas = [re.sub(r"\[[^\]]*\]", "", l).strip() for l in fh if l.strip()]
    lista = lambda sub, ext: sorted(f for f in os.listdir(os.path.join(P, sub)) if f.lower().endswith(ext)) \
        if os.path.isdir(os.path.join(P, sub)) else []
    clips = {os.path.splitext(f)[0]: f"clips/{f}" for f in lista("clips", (".mp4", ".mov", ".webm", ".mkv"))}
    imgs = {os.path.splitext(f)[0]: f"imagenes/{f}" for f in lista("imagenes", (".png", ".webp", ".jpg", ".jpeg"))}
    poses = [os.path.splitext(f)[0] for f in lista("personaje", (".png", ".webp"))]
    palabra = a.palabra
    if not palabra:
        m = re.search(r"[Cc]omenta\s+\**([A-ZÁÉÍÓÚÑ0-9]+)", lineas[-1])
        palabra = limpia(m.group(1)) if m else None
    es_cta = bool(re.search(r"coment|s[ií]gueme|escr[ií]beme|suscr[ií]b", lineas[-1].lower()))
    if palabra and not es_cta:
        print(f"  Aviso: la última frase del guion no es una llamada a la acción («Comenta {palabra}…»). "
              "La dejo como frase normal: si quieres el final con la palabra, añádelo al guion y a la voz.")
    if a.dos_finales and not (palabra and es_cta):
        print("  Aviso: --dos-finales necesita que la última frase sea «Comenta PALABRA…»: no añado final_tiktok.")
    plan = {"nombre": os.path.basename(os.path.abspath(P)), "estilo": "arena", "voz": "voz", "clips": clips, "imagenes": imgs}
    if a.fuente:
        plan["fuente_clips"] = a.fuente
    if poses:
        plan["personaje"] = {"carpeta": "personaje", "pose": poses[0]}
    medios = [("clip", k) for k in clips] + [("imagen", k) for k in imgs]

    def medio_para(linea, i):
        """El clip o la imagen cuyo nombre comparte una palabra con la frase; si no, el siguiente de la lista."""
        palabras = {normaliza(limpia(p)) for p in linea.split() if len(normaliza(limpia(p))) > 3}
        for tipo, clave in medios:
            trozos = {normaliza(x) for x in re.split(r"[_\-\s]+", clave) if len(x) > 3}
            if palabras & trozos or any(p.startswith(t) or t.startswith(p) for p in palabras for t in trozos):
                return tipo, clave
        return medios[i % len(medios)]
    frases = []
    for i, l in enumerate(lineas):
        f = {"titular": titular(l), "elementos": []}
        if poses:
            f["pose"] = poses[i % len(poses)]
        ultima = i == len(lineas) - 1
        if ultima and palabra and es_cta:
            f["titular"] = ["COMENTA"]
            f["elementos"] = [{"tipo": "palabra", "texto": palabra.upper(), "x": 540, "y": 760},
                              {"tipo": "icono", "nombre": "regalo", "x": 540, "y": 1080, "ancho": 240}]
        else:
            if medios:
                tipo, clave = medio_para(l, i)
                f["elementos"].append({"tipo": tipo, "src": clave, "x": 540, "y": 760})
            grupos = negritas(l)
            if len(grupos) > 1:
                f["elementos"].append({"tipo": "etiqueta", "texto": limpia(grupos[-1]).upper(), "fondo": "acento",
                                       "en": normaliza(grupos[-1].split()[0]), "x": 560, "y": 1130})
            elif not medios:
                f["elementos"].append({"tipo": "icono", "nombre": "estrella", "x": 540, "y": 820, "ancho": 300})
        if i > 0 and i % 4 == 0:
            f["transicion"] = "papel"
        frases.append(f)
    plan["frases"] = frases
    if palabra and es_cta and a.dos_finales:
        plan["final_tiktok"] = {"titular": ["SÍGUEME"],
                                "elementos": [{"tipo": "palabra", "texto": palabra.upper(), "x": 540, "y": 760},
                                              {"tipo": "etiqueta", "texto": "escríbeme por privado", "x": 540, "y": 1080}]}
    plan["portada"] = {"etiqueta": "UNA HISTORIA", "linea": titular(lineas[0])[0].lower(), "grande": (palabra or (re.findall(r"\d[\d.,]*", lineas[0]) or [titular(lineas[0])[0].split()[0]])[0]).upper(),
                       "remate": "te lo cuento", **({"imagen": next(iter(imgs))} if imgs else ({"clip": next(iter(clips)), "segundo": 1.0} if clips else {})),
                       **({"pose": poses[0]} if poses else {})}
    guardar_json(destino, plan)
    print(f"Borrador: {destino} ({len(frases)} frases, {len(clips)} clips, {len(imgs)} imágenes, {len(poses)} poses)")
    print("Siguiente: render.py --muestras, mira la hoja y mejora el plan (referencias/plan.md).")


if __name__ == "__main__":
    main()
