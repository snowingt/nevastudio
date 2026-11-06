"""Saca el texto para generar la voz del reel (ElevenLabs u otra) a partir de src/datos/plan.json.

Uso:
  python3 voz.py --proyecto ~/reel                   texto con etiquetas de emoción para ElevenLabs (modelo v3)
  python3 voz.py --proyecto ~/reel --sin-etiquetas   texto limpio (para grabarlo uno mismo o para otras voces)

Cada frase va en su propia línea, sin asteriscos, con su etiqueta de emoción delante ([excited], [curious]…)
y con el texto de "voz" si la frase lo tiene (para que pronuncie bien nombres: Claude → Clod).
Lo guarda también en salida/voz.txt para poder mandárselo al usuario como archivo.
"""
import argparse
import json
import os
import re
import sys

PASOS = """CÓMO GENERAR LA VOZ EN ELEVENLABS
1. Entra en elevenlabs.io → Text to Speech.
2. Modelo: Eleven v4 (o Eleven v3 si no te sale): son los que entienden las etiquetas entre corchetes.
3. Elige una voz en español (en Voice Library puedes filtrar por acento de España o de Latinoamérica).
4. Pega el texto de abajo tal cual, con las etiquetas.
5. Genera, escúchalo y, si te gusta, descarga el MP3 (o WAV) y súbelo al chat.
   (Si una frase sale rara, vuelve a generar: cada toma sale distinta.)
6. Al publicar el reel, márcalo como contenido hecho con IA (Instagram y TikTok lo piden si la voz es de IA)."""

PASOS_GRABAR = """CÓMO GRABAR LA VOZ
1. Graba con el móvil en un sitio sin eco (un armario con ropa va genial), a 15–20 cm del micro.
2. Lee el texto de abajo con energía y sin pausas largas entre frases (las pausas se recortan solas).
3. Manda el audio al chat (vale m4a, mp3, wav, ogg…)."""


def limpiar(t):
    t = t.replace("*", "")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proyecto", default=".")
    ap.add_argument("--sin-etiquetas", action="store_true")
    a = ap.parse_args()
    proy = os.path.abspath(os.path.expanduser(a.proyecto))
    ruta = os.path.join(proy, "src", "datos", "plan.json")
    if not os.path.exists(ruta):
        sys.exit(f"No encuentro {ruta}. ¿Has ejecutado preparar.py y escrito el plan?")
    plan = json.load(open(ruta, encoding="utf-8"))
    lineas = []
    for k, fr in enumerate(plan.get("frases", []), start=1):
        texto = limpiar(fr.get("voz") or fr.get("texto", ""))
        if not texto:
            sys.exit(f"La frase {k} no tiene texto")
        emo = (fr.get("emocion") or "").strip()
        if emo and not a.sin_etiquetas:
            if not (emo.startswith("[") and emo.endswith("]")):
                emo = f"[{emo.strip('[]')}]"
            texto = f"{emo} {texto}"
        lineas.append(texto)
    cuerpo = "\n".join(lineas)
    palabras = sum(len(limpiar(fr.get("voz") or fr.get("texto", "")).split()) for fr in plan.get("frases", []))
    seg = palabras / 175 * 60  # el mismo ritmo que alinear.py --sin-voz
    cabecera = PASOS_GRABAR if a.sin_etiquetas else PASOS
    salida = f"{cabecera}\n\nTEXTO ({palabras} palabras, unos {seg:.0f} s de voz):\n\n{cuerpo}\n"
    os.makedirs(os.path.join(proy, "salida"), exist_ok=True)
    destino = os.path.join(proy, "salida", "voz.txt")
    open(destino, "w", encoding="utf-8").write(salida)
    print(salida)
    print(f"(guardado en {destino})")
    if seg > 75:
        print("AVISO: pasa de 75 s de voz. Para reels funciona mejor 25–60 s: recorta frases antes de generar la voz.")


if __name__ == "__main__":
    main()
