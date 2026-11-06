#!/usr/bin/env python3
"""Versión con las citas originales: algunas frases suenan con el audio del clip en lugar de tu voz.

Uso:
  python3 scripts/citas.py --voz P/voz --citas P/citas.json --salida P/voz_b [--idioma es]
  python3 scripts/render.py P/video.json --voz voz_b --sufijo b

citas.json es una lista. Cada cita:
  {"frase": 4,                      número de frase del guion (empieza en 1)
   "clip": "originales/c1.mp4",     el clip CON audio (ruta relativa a citas.json)
   "tramos": [[105.4, 107.6]],      segundos del clip que suenan (uno o varios; entre tramos, como mucho --pausa)
   "texto": "Lo que dice el personaje.",   lo que se oye: sale en los subtítulos
   "desde": "vete", "hasta": "solo"  palabras de TU guion que sustituye (si no se ponen, la frase entera)
   "despues": "cohete"}              en lugar de sustituir, la mete detrás de esa palabra (y no quita nada)

La voz de las citas se iguala a −14 LUFS para que suene tan fuerte como la tuya. Si el audio del clip lleva música,
también se oye: usa tramos cortos. Escribe en "texto" lo que dice el audio de verdad (compruébalo con trozos.py transcribir).
"""
import argparse, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alinear as al  # noqa: E402
from comun import FFMPEG, cargar_json, guardar_json, normaliza, limpia  # noqa: E402

SR = 48000


def audio_cita(cita, base_dir, pausa, tmpdir):
    ruta = cita["clip"] if os.path.isabs(cita["clip"]) else os.path.join(base_dir, cita["clip"])
    if not os.path.exists(ruta):
        sys.exit(f"No encuentro el clip de la cita: {ruta}")
    trozos = []
    for k, (t0, t1) in enumerate(cita["tramos"]):
        raw = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", ruta, "-vn",
                              "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
        a = np.frombuffer(raw, np.float32).copy()
        if len(a) == 0:
            sys.exit(f"El clip {ruta} no tiene audio en {t0}–{t1} s.")
        # ¿el tramo empieza o acaba en mitad de una palabra? (voz fuerte en los bordes)
        v = int(SR * 0.06)
        rms = lambda x: float(np.sqrt(np.mean(x ** 2) + 1e-12))
        nivel = np.percentile(np.abs(a), 90) + 1e-9
        for borde, trozo in (("acaba", a[-v:]), ("empieza", a[:v])):
            if len(a) > 4 * v and rms(trozo) > 0.35 * nivel:
                print(f"  AVISO: el tramo {t0}–{t1} s {borde} con voz: puede cortar una palabra. "
                      f"{'Alarga el final' if borde == 'acaba' else 'Adelanta el principio'} unas décimas y repite.")
        f = int(SR * 0.02)
        a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
        if k:
            trozos.append(np.zeros(int(pausa * SR), np.float32))
        trozos.append(a)
    a = np.concatenate(trozos)
    tmp = os.path.join(tmpdir, "_cita.wav"); norm = os.path.join(tmpdir, "_cita_norm.wav")
    al.escribir_wav(tmp, a, SR)
    al.normalizar(tmp, norm)
    out = al.leer_audio(norm, SR)
    os.remove(tmp); os.remove(norm)
    return out, ruta


def palabras_cita(texto, audio, idioma, modelo):
    script = al.tokens([texto])
    a16 = np.interp(np.arange(0, len(audio), SR / al.SR), np.arange(len(audio)), audio).astype(np.float32)
    oidas = al.reconocer(a16, idioma, modelo)
    if oidas:
        cal = al.emparejar(script, oidas)
        oido = " ".join(w["n"] for w in oidas)
        print(f"  Cita «{texto[:50]}»: se oye «{oido[:90]}» ({cal * 100:.0f} % de coincidencia)")
        if cal < 0.85 or len(oidas) > len(script) + 1:
            print("  AVISO: \"texto\" no coincide con lo que se oye (faltan o sobran palabras). "
                  "Corrígelo para que los subtítulos digan lo mismo que el audio, o ajusta \"tramos\".")
    else:
        al.por_energia(script, a16, al.SR)
    return script


def busca(ws, palabra, desde=0):
    n = normaliza(palabra)
    for k in range(desde, len(ws)):
        if normaliza(limpia(ws[k]["t"])) == n:
            return k
    for k in range(desde, len(ws)):
        if normaliza(limpia(ws[k]["t"])).startswith(n):
            return k
    sys.exit(f"No encuentro la palabra «{palabra}» en esa frase del guion.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--voz", required=True)
    ap.add_argument("--citas", required=True)
    ap.add_argument("--salida", required=True)
    ap.add_argument("--idioma", default="es")
    ap.add_argument("--pausa", type=float, default=0.6, help="pausa máxima entre dos tramos de una misma cita")
    ap.add_argument("--modelo")
    a = ap.parse_args()
    datos = cargar_json(os.path.join(a.voz, "palabras.json"))
    citas = cargar_json(a.citas)
    base_dir = os.path.dirname(os.path.abspath(a.citas))
    os.makedirs(a.salida, exist_ok=True)
    voz = al.leer_audio(os.path.join(a.voz, "voz_final.wav"), SR)
    pal = datos["palabras"]

    # cada cita se convierte en una operación sobre la línea de tiempo: [t_quita0, t_quita1) se cambia por el audio de la cita
    ops = []
    for c in citas:
        i = int(c["frase"]) - 1
        ws_idx = [k for k, w in enumerate(pal) if w["frase"] == i]
        if not ws_idx:
            sys.exit(f"La frase {c['frase']} no existe en la voz.")
        ws = [pal[k] for k in ws_idx]
        audio, ruta = audio_cita(c, base_dir, a.pausa, a.salida)
        script = palabras_cita(c["texto"], audio, a.idioma, a.modelo)
        if c.get("despues"):
            k = busca(ws, c["despues"])
            sig = pal[ws_idx[k] + 1]["ini"] if ws_idx[k] + 1 < len(pal) else ws[k]["fin"] + 1
            t = min(ws[k]["fin"] + 0.04, (ws[k]["fin"] + sig) / 2)  # en la pausa, sin pisar la palabra siguiente
            ops.append({"t0": t, "t1": t, "audio": audio, "aire": 0.14, "frase": i, "quita": [], "tras": ws_idx[k],
                        "script": script, "clip": ruta, "tramos": c["tramos"], "texto": c["texto"]})
        else:
            k0 = busca(ws, c["desde"]) if c.get("desde") else 0
            k1 = busca(ws, c["hasta"], k0) if c.get("hasta") else len(ws) - 1
            ant = pal[ws_idx[k0] - 1]["fin"] if ws_idx[k0] > 0 else 0.0
            sig = pal[ws_idx[k1] + 1]["ini"] if ws_idx[k1] + 1 < len(pal) else ws[k1]["fin"] + 1
            t0 = max(ws[k0]["ini"] - 0.04, (ant + ws[k0]["ini"]) / 2)
            t1 = min(ws[k1]["fin"] + 0.04, (ws[k1]["fin"] + sig) / 2)
            ops.append({"t0": t0, "t1": t1, "audio": audio, "aire": 0.06, "frase": i, "quita": ws_idx[k0:k1 + 1],
                        "tras": ws_idx[k0] - 1, "script": script, "clip": ruta, "tramos": c["tramos"], "texto": c["texto"]})
    ops.sort(key=lambda o: o["t0"])

    partes, pos, desplaza = [], 0.0, 0.0
    mapa = []  # (t_original_ini, t_original_fin, desplazamiento) para lo que no se toca
    for o in ops:
        partes.append(voz[int(pos * SR):int(o["t0"] * SR)])
        mapa.append((pos, o["t0"], desplaza))
        aire = np.zeros(int(o["aire"] * SR), np.float32)
        o["nuevo_t0"] = o["t0"] + desplaza + o["aire"]
        partes += [aire, o["audio"], aire]
        dur_cita = len(o["audio"]) / SR
        desplaza += 2 * o["aire"] + dur_cita - (o["t1"] - o["t0"])
        o["nuevo_t1"] = o["nuevo_t0"] + dur_cita
        pos = o["t1"]
    partes.append(voz[int(pos * SR):])
    mapa.append((pos, 1e9, desplaza))
    total = np.concatenate(partes)
    al.escribir_wav(os.path.join(a.salida, "voz_final.wav"), total, SR)

    def mueve(t):
        for t0, t1, d in mapa:
            if t0 - 1e-6 <= t < t1:
                return t + d
        return t + desplaza

    nuevas = []
    quitadas = {k: o for o in ops for k in o["quita"]}
    for k, w in enumerate(pal):
        if k in quitadas:
            o = quitadas[k]
            # las palabras sustituidas se reparten por la cita: así los elementos anclados a ellas siguen en su sitio
            q = o["quita"]
            j = q.index(k)
            d = o["nuevo_t1"] - o["nuevo_t0"]
            nuevas.append(dict(w, ini=round(o["nuevo_t0"] + d * j / len(q), 3), fin=round(o["nuevo_t0"] + d * (j + 1) / len(q), 3)))
        else:
            nuevas.append(dict(w, ini=round(mueve(w["ini"]), 3), fin=round(mueve(w["fin"]), 3)))
    frases = []
    for i, f in enumerate(datos["frases"]):
        ws = [w for w in nuevas if w["frase"] == i]
        f2 = dict(f, ini=ws[0]["ini"], fin=ws[-1]["fin"])
        mis = [o for o in ops if o["frase"] == i]
        if mis:
            # subtítulos: tu guion fuera de la cita + lo que dice el audio dentro
            subs = [w for k, w in enumerate(nuevas) if w["frase"] == i and k not in quitadas]
            info = []
            for o in mis:
                for w in o["script"]:
                    subs.append({"t": w["t"], "ini": round(o["nuevo_t0"] + w["ini"], 3), "fin": round(o["nuevo_t0"] + w["fin"], 3)})
                info.append({"t0": round(o["nuevo_t0"], 3), "t1": round(o["nuevo_t1"], 3),
                             "clip": os.path.relpath(o["clip"], os.path.abspath(a.salida)),
                             "desde": o["tramos"][0][0], "texto": o["texto"]})
            subs.sort(key=lambda w: w["ini"])
            f2["subtitulo"] = subs
            f2["citas"] = info
            f2["fin"] = max(f2["fin"], max(x["t1"] for x in info))
        frases.append(f2)
    dur = len(total) / SR
    guardar_json(os.path.join(a.salida, "palabras.json"), {"fuente": datos.get("fuente"), "duracion": round(dur, 3),
                                                          "voz": "voz_final.wav", "frases": frases, "palabras": nuevas})
    print(f"Listo: {a.salida} ({dur:.1f} s; {len(ops)} cita(s); antes {datos['duracion']:.1f} s)")


if __name__ == "__main__":
    main()
