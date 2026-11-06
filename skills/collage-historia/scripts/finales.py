#!/usr/bin/env python3
"""Segundo final (por ejemplo, el de TikTok) sin volver a grabar ni a montar todo el vídeo.

Uso:
  python3 scripts/finales.py --voz P/voz --final audio_final_tiktok.mp3 --texto "Sígueme y escríbeme HISTORIA por privado." \
                             --salida P/voz_tiktok [--idioma es]

Coge la voz ya alineada (P/voz), la corta justo antes de la última frase y pega el audio del otro final
con 0,12 s de silencio. Deja en --salida la voz_final.wav y el palabras.json del segundo final.
Después: render.py P/video.json --final tiktok (el cuerpo del vídeo se reutiliza; solo se monta el final).
"""
import argparse, os, re, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alinear as al  # noqa: E402
from comun import cargar_json, guardar_json  # noqa: E402

SR = 48000


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--voz", required=True, help="carpeta de la voz principal ya alineada (con palabras.json)")
    ap.add_argument("--final", help="audio del otro final (solo la última frase)")
    ap.add_argument("--texto", required=True, help="texto exacto del otro final (puede llevar **palabras clave**)")
    ap.add_argument("--salida", required=True)
    ap.add_argument("--idioma", default="es")
    ap.add_argument("--silencio", type=float, default=0.12)
    ap.add_argument("--modelo")
    a = ap.parse_args()
    datos = cargar_json(os.path.join(a.voz, "palabras.json"))
    os.makedirs(a.salida, exist_ok=True)
    frases = datos["frases"]
    ult = len(frases) - 1
    if not re.search(r"coment|s[ií]gueme|escr[ií]beme|suscr[ií]b", frases[ult]["texto"].lower()):
        print(f"  AVISO: la última frase de la voz es «{frases[ult]['texto'][:60]}», que no parece un final "
              "(«Comenta…»). finales.py sustituye la ÚLTIMA frase: el guion tiene que acabar en el final de Instagram.")
    previas = [w for w in datos["palabras"] if w["frase"] < ult]
    texto = " ".join(a.texto.replace("\n", " ").split())
    script = al.tokens([texto])
    for w in script:
        w["frase"] = ult

    voz_ruta = os.path.join(a.voz, "voz_final.wav")
    if datos.get("voz") and os.path.exists(voz_ruta):
        if not a.final:
            sys.exit("La voz principal tiene audio: pasa también --final con el audio del otro final.")
        corte = max(previas[-1]["fin"] + 0.03, frases[ult]["ini"] - 0.06) if previas else 0.0
        base = al.leer_audio(voz_ruta, SR)[:int(corte * SR)]
        f = int(SR * 0.01)
        if len(base) > f:
            base[-f:] *= np.linspace(1, 0, f)
        fin = al.leer_audio(a.final, SR)
        fin, _ = al.recortar_pausas(fin, SR, 0.26)
        tmp = os.path.join(a.salida, "_final.wav")
        al.escribir_wav(tmp, fin, SR)
        norm = os.path.join(a.salida, "_final_norm.wav")
        al.normalizar(tmp, norm)
        fin = al.leer_audio(norm, SR)
        os.remove(tmp)
        desplaza = len(base) / SR + a.silencio
        a16 = al.leer_audio(norm, al.SR)
        oidas = al.reconocer(a16, a.idioma, a.modelo)
        if oidas:
            calidad = al.emparejar(script, oidas)
            print(f"  Palabras del final reconocidas: {calidad * 100:.0f} %")
        else:
            al.por_energia(script, a16, al.SR)
        os.remove(norm)
        total = np.concatenate([base, np.zeros(int(a.silencio * SR), np.float32), fin])
        al.escribir_wav(os.path.join(a.salida, "voz_final.wav"), total, SR)
        dur = len(total) / SR
        voz = "voz_final.wav"
    else:
        # sin voz: tiempos estimados a partir de la última frase de la voz principal
        desplaza = frases[ult]["ini"]
        al.estimar(script, 185)
        t0 = script[0]["ini"]
        for w in script:
            w["ini"] -= t0; w["fin"] -= t0
        dur = desplaza + script[-1]["fin"] + 0.6
        voz = None
    for w in script:
        w["ini"] = round(w["ini"] + desplaza, 3); w["fin"] = round(w["fin"] + desplaza, 3)
    nuevas = frases[:-1] + [{"texto": texto, "ini": script[0]["ini"], "fin": script[-1]["fin"]}]
    pal = previas + [{"t": w["t"], "ini": w["ini"], "fin": w["fin"], "frase": ult} for w in script]
    guardar_json(os.path.join(a.salida, "palabras.json"), {"fuente": datos.get("fuente"), "duracion": round(dur, 3),
                                                          "voz": voz, "frases": nuevas, "palabras": pal})
    print(f"Listo: {a.salida} ({dur:.1f} s; el cuerpo es igual hasta {nuevas[-1]['ini']:.2f} s)")


if __name__ == "__main__":
    main()
