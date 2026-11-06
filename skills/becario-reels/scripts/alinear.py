"""Prepara la voz del reel y saca el momento exacto de cada palabra.

Uso:
  python3 alinear.py VOZ.mp3 --proyecto ~/reel            con voz (ElevenLabs, grabada con el móvil, etc.)
  python3 alinear.py --sin-voz --proyecto ~/reel          sin voz: tiempos a ritmo de lectura (reel solo con texto)

Opciones:
  --pausa 0.26   ninguna pausa dentro de la voz dura más de esto (los reels que funcionan no dejan huecos)
  --tempo 1.0    acelera o frena la voz sin cambiar el tono (1.05 = 5 % más rápida)
  --cola 1.5     segundos de silencio al final (la llamada a la acción se queda en pantalla)
  --motor auto   "silabas" (sin descargas; reparte por sílabas dentro de cada frase y ajusta a la energía de la voz),
                 "asr" (reconocimiento de voz con Parakeet; más exacto, pero descarga ~470 MB) o "auto"
  --ppm 175      sin voz: palabras por minuto

Lee las frases de src/datos/plan.json ("texto", con las palabras clave entre *asteriscos*).
Escribe public/voz.wav (mono, -14 LUFS, pausas recortadas) y src/datos/tiempos.json.
"""
import argparse
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import wave

import numpy as np

SR = 48000
VENTANA = 0.01  # s, para la envolvente de energía


# ---------------------------------------------------------------- ffmpeg

def buscar_ffmpeg(proyecto):
    """ffmpeg del sistema, el que trae Remotion en node_modules o el de imageio-ffmpeg."""
    if shutil.which("ffmpeg"):
        return "ffmpeg", dict(os.environ)
    base = os.path.join(proyecto, "node_modules", "@remotion")
    if os.path.isdir(base):
        for d in sorted(os.listdir(base)):
            if d.startswith("compositor-"):
                b = os.path.join(base, d, "ffmpeg")
                if os.path.exists(b):
                    env = dict(os.environ)
                    env["LD_LIBRARY_PATH"] = os.path.join(base, d) + ":" + env.get("LD_LIBRARY_PATH", "")
                    env["DYLD_LIBRARY_PATH"] = os.path.join(base, d)
                    return b, env
    try:
        import imageio_ffmpeg  # type: ignore

        return imageio_ffmpeg.get_ffmpeg_exe(), dict(os.environ)
    except Exception:
        pass
    sys.exit("No encuentro ffmpeg. Ejecuta antes scripts/preparar.py (instala la plantilla) o: pip install imageio-ffmpeg")


def ff(proyecto, args, entrada=None):
    b, env = buscar_ffmpeg(proyecto)
    return subprocess.run([b, "-hide_banner", "-loglevel", "error", *args], input=entrada, capture_output=True, env=env, check=True).stdout


def decodificar(proyecto, ruta, tempo):
    filtros = ["aresample=48000"] + ([f"atempo={tempo}"] if abs(tempo - 1) > 1e-3 else [])
    raw = ff(proyecto, ["-i", ruta, "-ac", "1", "-af", ",".join(filtros), "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, dtype=np.float32).copy()


def guardar_wav(ruta, x):
    y = x / (np.abs(x).max() + 1e-9) * 0.9
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())


# ---------------------------------------------------------------- energía y pausas

def envolvente_db(x):
    n = int(VENTANA * SR)
    k = len(x) // n
    rms = np.sqrt((x[: k * n].reshape(k, n) ** 2).mean(axis=1) + 1e-12)
    return 20 * np.log10(rms + 1e-12)


def umbral_de(db):
    # 32 dB por debajo de los picos de la voz (o -52 dBFS como mínimo): separa bien voz y silencio
    return max(np.percentile(db, 95) - 32, -52)


def tramos_silencio(db, umbral, minimo):
    bajo = db < umbral
    out, i = [], 0
    while i < len(bajo):
        if bajo[i]:
            j = i
            while j < len(bajo) and bajo[j]:
                j += 1
            if (j - i) * VENTANA >= minimo:
                out.append((i, j))
            i = j
        else:
            i += 1
    return out


def acortar_pausas(x, pausa):
    """Quita el silencio del principio y del final y deja cada pausa interna en como mucho `pausa` segundos."""
    db = envolvente_db(x)
    u = umbral_de(db)
    voz = np.where(db >= u)[0]
    if len(voz) == 0:
        sys.exit("El audio parece vacío (no hay voz)")
    n = int(VENTANA * SR)
    x = x[max(0, voz[0] - 2) * n : min(len(x), (voz[-1] + 3) * n)]
    db = envolvente_db(x)
    trozos, ultimo = [], 0
    fundido = int(0.006 * SR)
    for i, j in tramos_silencio(db, u, pausa + 0.02):
        quitar = (j - i) * VENTANA - pausa
        if quitar <= 0:
            continue
        medio = (i + j) / 2 * n
        q0, q1 = int(medio - quitar * SR / 2), int(medio + quitar * SR / 2)
        t = x[ultimo:q0].copy()
        if len(t) > fundido:
            t[-fundido:] *= np.linspace(1, 0, fundido)
        trozos.append(t)
        ultimo = q1
    trozos.append(x[ultimo:])
    for k in range(1, len(trozos)):
        if len(trozos[k]) > fundido:
            trozos[k][:fundido] *= np.linspace(0, 1, fundido)
    return np.concatenate(trozos)


def paso_alto(x, fc=70.0):
    """Filtro paso alto de primer orden (quita retumbe y golpes de micro)."""
    rc = 1 / (2 * np.pi * fc)
    a = rc / (rc + 1 / SR)
    try:
        from scipy.signal import lfilter  # type: ignore

        return lfilter([a, -a], [1, -a], x).astype(np.float32)
    except Exception:
        y = np.empty_like(x)
        y[0] = x[0]
        for i in range(1, len(x)):
            y[i] = a * (y[i - 1] + x[i] - x[i - 1])
        return y


# ---------------------------------------------------------------- texto

UNIDADES = "cero uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciséis diecisiete dieciocho diecinueve veinte".split()
DECENAS = {30: "treinta", 40: "cuarenta", 50: "cincuenta", 60: "sesenta", 70: "setenta", 80: "ochenta", 90: "noventa"}
CENTENAS = {100: "ciento", 200: "doscientos", 300: "trescientos", 400: "cuatrocientos", 500: "quinientos", 600: "seiscientos", 700: "setecientos", 800: "ochocientos", 900: "novecientos"}


def numero_a_palabras(n):
    """Número en palabras (español), para contar sílabas y comparar con lo que se oye."""
    if n <= 20:
        return UNIDADES[n]
    if n < 30:
        return "veinti" + UNIDADES[n - 20]
    if n < 100:
        d, u = n // 10 * 10, n % 10
        return DECENAS[d] + ("" if u == 0 else " y " + UNIDADES[u])
    if n == 100:
        return "cien"
    if n < 1000:
        c, r = n // 100 * 100, n % 100
        return CENTENAS[c] + ("" if r == 0 else " " + numero_a_palabras(r))
    if n < 1_000_000:
        m, r = n // 1000, n % 1000
        return ("mil" if m == 1 else numero_a_palabras(m) + " mil") + ("" if r == 0 else " " + numero_a_palabras(r))
    return str(n)


def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def hablado(w):
    """Cómo suena una palabra escrita (cifras en letras, con %, € o $ y decimales con coma)."""
    limpio = re.sub(r"[^\w%€$,]", "", w).rstrip(",")
    m = re.fullmatch(r"(\d[\d.]*)(?:,(\d+))?([%€$]?)", limpio)
    if m:
        s = numero_a_palabras(int(m.group(1).replace(".", "")))
        if m.group(2):
            s += " coma " + numero_a_palabras(int(m.group(2)))
        return s + {"%": " por ciento", "€": " euros", "$": " dólares", "": ""}[m.group(3)]
    return {"%": "por ciento", "€": "euros", "$": "dólares"}.get(limpio, w)


def silabas(w):
    return max(1, len(re.findall(r"[aeiouáéíóúü]+", hablado(w).lower())))


def fonetica(w):
    w = sin_tildes(hablado(w).lower())
    w = re.sub(r"[^a-zñ0-9 ]", "", w).replace(" ", "")
    for a, b in [("ll", "y"), ("qu", "k"), ("ce", "se"), ("ci", "si"), ("c", "k"), ("z", "s"), ("v", "b"), ("h", ""), ("w", "u"), ("ee", "i"), ("au", "o"), ("x", "ks")]:
        w = w.replace(a, b)
    return w


def palabras_frase(texto):
    """[(palabra, clave, grupo)] sin [etiquetas]; las que van entre *asteriscos* son clave y forman un grupo."""
    texto = re.sub(r"\[[^\]]*\]", " ", texto)
    out, dentro, g = [], False, -1
    for w in texto.split():
        if w.startswith("*"):
            dentro = True
            palabras_frase.grupo += 1
            g = palabras_frase.grupo
        limpia = w.replace("*", "")
        if limpia in ("%", "€", "$") and out:
            # «80 %» o «1.500 €»: el símbolo va con su número (con espacio que no se parte)
            prev = out[-1]
            out[-1] = (prev[0] + "\u00a0" + limpia, prev[1] or dentro, prev[2] if prev[1] else (g if dentro else -1))
        elif limpia:
            out.append((limpia, dentro, g if dentro else -1))
        if w.rstrip(".,:;!?…").endswith("*"):
            dentro = False
    return out


palabras_frase.grupo = -1


# ---------------------------------------------------------------- motor "silabas" (sin modelos)

def limites_frases(db, u, sil_frase, habla, esperado=None, sigma=0.6):
    """Inicio y fin de la voz de cada frase. Cada corte entre frases cae en una pausa real de la voz (la que mejor
    encaja con el reparto por sílabas, o con lo reconocido si se pasa `esperado`) o, si no hay ninguna pausa cerca,
    justo donde toca: así una frase partida donde la voz no para no descoloca a todas las demás."""
    nf = len(sil_frase)
    voz = np.where(db >= u)[0]
    B0, E1 = voz[0] * VENTANA, (voz[-1] + 1) * VENTANA
    if nf == 1:
        return [B0], [E1]
    pausas = [(a * VENTANA, b * VENTANA) for a, b in tramos_silencio(db, u, 0.07)]
    tot = sum(sil_frase)
    if esperado is None:
        esperado = [B0 + (E1 - B0) * sum(sil_frase[: k + 1]) / tot for k in range(nf - 1)]
    K = nf - 1
    VIRTUAL = 2.2  # coste de cortar sin pausa: como una pausa larga a ~1 s de donde toca
    # candidatos de cada corte: todas las pausas reales y un corte "virtual" justo en lo esperado
    cand = []
    for k in range(K):
        c_k = [(s0, s1, ((s0 - esperado[k]) / sigma) ** 2 - 2.0 * min(s1 - s0, 0.4)) for s0, s1 in pausas]
        c_k.append((esperado[k] - 0.03, esperado[k] + 0.03, VIRTUAL))
        cand.append(c_k)
    D = [np.array([c for _, _, c in cand[0]])]
    P = [None]
    for k in range(1, K):
        dk = np.full(len(cand[k]), np.inf)
        pk = np.full(len(cand[k]), -1, dtype=int)
        for j, (q0, _, cq) in enumerate(cand[k]):
            for i, (_, p1, _) in enumerate(cand[k - 1]):
                if q0 > p1 + 0.25 and D[k - 1][i] + cq < dk[j]:
                    dk[j], pk[j] = D[k - 1][i] + cq, i
        D.append(dk)
        P.append(pk)
    j = int(np.argmin(D[K - 1]))
    if not np.isfinite(D[K - 1][j]):  # no hay forma ordenada: se corta donde toca por sílabas
        elegidos = [(t - 0.03, t + 0.03) for t in esperado]
    else:
        idx = [j]
        for k in range(K - 1, 0, -1):
            j = int(P[k][j])
            idx.append(j)
        idx.reverse()
        elegidos = [(cand[k][i][0], cand[k][i][1]) for k, i in enumerate(idx)]
    B, E = [B0], []
    for s0, s1 in elegidos:
        E.append(s0)
        B.append(s1)
    E.append(E1)
    return B, E


def avisos_ritmo(B, E, sil_frase, textos):
    """Frases que van mucho más rápidas o más lentas que el resto: casi siempre, un corte mal puesto."""
    vel = [s / max(0.2, e - b) for s, b, e in zip(sil_frase, B, E)]
    if len(vel) < 3:
        return []
    med = float(np.median(vel))
    out = []
    for k, v in enumerate(vel):
        if v > med * 1.45 or v < med * 0.55:
            out.append(f"AVISO: la frase {k + 1} («{textos[k][:40]}…») va a {v:.1f} sílabas/s y la media es {med:.1f}. "
                       "Puede que su principio o su final esté en la frase de al lado: escucha esa parte. Si partiste una "
                       "frase donde la voz no hace pausa, júntala otra vez.")
    return out


def tiempos_por_silabas(x, frases_pal, esperado=None, sigma=0.6):
    """Sin modelos: cada frase va de pausa real a pausa real; dentro, las sílabas se reparten por el tiempo
    en que hay voz (las comas y respiraciones no cuentan) y cada palabra empieza 70 ms antes del centro de
    su primera sílaba. Medido contra reconocimiento de voz: unos 70 ms de error típico y 0,2 s en el peor 10 %."""
    db = envolvente_db(x)
    u = umbral_de(db)
    habla = len(x) / SR
    sil_frase = [sum(silabas(w) for w, _, _ in fp) for fp in frases_pal]
    B, E = limites_frases(db, u, sil_frase, habla, esperado, sigma)
    # la voz arranca un poco antes de pasar el umbral (consonantes suaves): adelanta inicios y retrasa finales
    B = [max(0.0, b - 0.06) if k > 0 else b for k, b in enumerate(B)]
    E = [e + 0.04 for e in E]
    tiempos = []
    for i, fp in enumerate(frases_pal):
        a, b = int(B[i] / VENTANA), max(int(B[i] / VENTANA) + 1, int(E[i] / VENTANA))
        voz = db[a:b] >= u
        acum = np.concatenate([[0], np.cumsum(voz)])
        total_voz = max(1, acum[-1])
        sil = [silabas(w) for w, _, _ in fp]
        S = sum(sil)
        ts, k = [], 0
        for j, n in enumerate(sil):
            objetivo = (k + 0.5) / S * total_voz
            idx = int(np.searchsorted(acum, objetivo, side="left"))
            centro = (a + min(idx, b - a)) * VENTANA
            ts.append(B[i] if j == 0 else centro - 0.07)
            k += n
        for j in range(1, len(ts)):
            ts[j] = max(ts[j], ts[j - 1] + 0.06)
        tiempos.append(ts)
    return B, E, tiempos


# ---------------------------------------------------------------- motor "asr" (Parakeet, opcional)

MODELO_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2"


def ruta_modelo():
    for d in [os.environ.get("BECARIO_ASR_MODELO", ""), os.path.expanduser("~/.cache/becario-reels/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8")]:
        if d and os.path.exists(os.path.join(d, "encoder.int8.onnx")):
            return d
    return None


def transcribir(x16, modelo):
    import sherpa_onnx  # type: ignore

    rec = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=f"{modelo}/encoder.int8.onnx", decoder=f"{modelo}/decoder.int8.onnx", joiner=f"{modelo}/joiner.int8.onnx", tokens=f"{modelo}/tokens.txt", model_type="nemo_transducer", num_threads=max(1, (os.cpu_count() or 2)),
    )
    s = rec.create_stream()
    s.accept_waveform(16000, x16)
    rec.decode_stream(s)
    words = []
    for tok, t in zip(s.result.tokens, s.result.timestamps):
        if tok.startswith(" ") or tok.startswith("▁") or not words:
            words.append([tok.strip().replace("▁", ""), float(t)])
        else:
            words[-1][0] += tok
    return [(w, t) for w, t in words if w.strip()]


def parecido(a, b):
    fa, fb = fonetica(a), fonetica(b)
    if not fa or not fb:
        return 0.0
    if min(len(fa), len(fb)) <= 2:
        return 1.0 if fa == fb else 0.0
    r = difflib.SequenceMatcher(a=fa, b=fb, autojunk=False).ratio()
    return r if r >= 0.6 else 0.0


def emparejar(guion, asr):
    n, m = len(guion), len(asr)
    sim = np.zeros((n, m))
    for i in range(n):
        c = int(i * m / max(n, 1))
        for j in range(max(0, c - 40), min(m, c + 40)):
            sim[i, j] = parecido(guion[i], asr[j])
    dp = np.zeros((n + 1, m + 1))
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dp[i, j] = max(dp[i - 1, j], dp[i, j - 1], dp[i - 1, j - 1] + sim[i - 1, j - 1] if sim[i - 1, j - 1] > 0 else -1)
    par = [None] * n
    i, j = n, m
    while i > 0 and j > 0:
        if sim[i - 1, j - 1] > 0 and abs(dp[i, j] - (dp[i - 1, j - 1] + sim[i - 1, j - 1])) < 1e-9:
            par[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif dp[i, j] == dp[i - 1, j]:
            i -= 1
        else:
            j -= 1
    return par


def tiempos_por_asr(x, frases_pal, modelo):
    t16 = np.arange(int(len(x) * 16000 / SR)) / 16000
    x16 = np.interp(t16, np.arange(len(x)) / SR, x).astype(np.float32)
    asr = transcribir(x16, modelo)
    plano = [w for fp in frases_pal for w, _, _ in fp]
    par = emparejar(plano, [w for w, _ in asr])
    t_asr = [asr[j][1] if j is not None else None for j in par]
    # cortes entre frases: donde empieza (según el reconocimiento) la primera palabra oída de la frase siguiente
    esperado, k, faltan = [], 0, 0
    for i, fp in enumerate(frases_pal[:-1]):
        k += len(fp)
        sig = frases_pal[i + 1]
        t = None
        for j in range(min(3, len(sig))):
            if t_asr[k + j] is not None:
                t = t_asr[k + j] - 0.05 - 0.25 * j
                break
        esperado.append(t)
        faltan += t is None
    if all(t is None for t in esperado):
        esperado = None
    else:
        # los que no se oyeron, por interpolación entre los oídos (o por sílabas en los extremos)
        sil = [sum(silabas(w) for w, _, _ in fp) for fp in frases_pal]
        acum = np.cumsum(sil)[:-1]
        conocidos = [(acum[i], t) for i, t in enumerate(esperado) if t is not None]
        xs, ys = [c[0] for c in conocidos], [c[1] for c in conocidos]
        esperado = [t if t is not None else float(np.interp(acum[i], xs, ys)) for i, t in enumerate(esperado)]
        for i in range(1, len(esperado)):
            esperado[i] = max(esperado[i], esperado[i - 1] + 0.3)
    B, E, t_sil = tiempos_por_silabas(x, frases_pal, esperado, 0.3)
    out, k = [], 0
    for i, fp in enumerate(frases_pal):
        ts = []
        for j in range(len(fp)):
            v = t_asr[k + j]
            ts.append(v if v is not None and B[i] - 0.15 <= v <= E[i] + 0.1 else t_sil[i][j])
        ts[0] = min(ts[0], B[i]) if t_asr[k] is None else ts[0]
        for j in range(1, len(ts)):
            ts[j] = max(ts[j], ts[j - 1] + 0.04)
        out.append(ts)
        k += len(fp)
    oidas = sum(t is not None for t in t_asr)
    usadas, k = 0, 0
    for i, fp in enumerate(frases_pal):
        usadas += sum(1 for j in range(len(fp)) if t_asr[k + j] is not None and B[i] - 0.15 <= t_asr[k + j] <= E[i] + 0.1)
        k += len(fp)
    asr_info = {"oidas": oidas, "usadas": usadas}
    return B, E, out, asr_info, asr


# ---------------------------------------------------------------- principal

def main():
    ap = argparse.ArgumentParser(description="Alinea la voz con las frases del plan y escribe tiempos.json")
    ap.add_argument("audio", nargs="?", help="la voz: mp3, wav, m4a, ogg… (o un vídeo)")
    ap.add_argument("--proyecto", default=".", help="carpeta del reel (la que creó preparar.py)")
    ap.add_argument("--sin-voz", action="store_true", help="reel sin voz: tiempos a ritmo de lectura")
    ap.add_argument("--pausa", type=float, default=0.26, help="ningún silencio dentro de la voz dura más de esto, en segundos (0.26)")
    ap.add_argument("--tempo", type=float, default=1.0, help="acelera o frena la voz sin cambiar el tono (1.05 = 5 %% más rápida)")
    ap.add_argument("--cola", type=float, default=1.5, help="segundos de vídeo después de la última palabra (1.5)")
    ap.add_argument("--ppm", type=float, default=175, help="sin voz: palabras por minuto (175)")
    ap.add_argument("--motor", choices=["auto", "silabas", "asr"], default="auto", help="silabas: sin descargas; asr: más exacto (necesita --descargar-modelo una vez); auto: asr si está")
    ap.add_argument("--descargar-modelo", action="store_true", help="descarga Parakeet v3 (~470 MB) e instala sherpa-onnx para el motor asr")
    a = ap.parse_args()

    if a.descargar_modelo:
        destino = os.path.expanduser("~/.cache/becario-reels")
        os.makedirs(destino, exist_ok=True)
        print("instalando sherpa-onnx…")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "sherpa-onnx==1.13.8"] + (["--break-system-packages"] if sys.prefix == sys.base_prefix else []), check=False)
        print(f"descargando el modelo (~470 MB) de {MODELO_URL} …")
        tar = os.path.join(destino, "modelo.tar.bz2")
        r = subprocess.run(["curl", "-fL", "-o", tar, MODELO_URL])
        if r.returncode != 0:
            sys.exit("No se pudo descargar (la red de este entorno puede no dejar). Sigue con --motor silabas: funciona sin descargas.")
        subprocess.run(["tar", "-xjf", tar, "-C", destino], check=True)
        os.remove(tar)
        print("listo: ya puedes usar --motor asr (o auto)")
        return

    proy = os.path.abspath(os.path.expanduser(a.proyecto))
    plan_ruta = os.path.join(proy, "src", "datos", "plan.json")
    if not os.path.exists(plan_ruta):
        sys.exit(f"No encuentro {plan_ruta}. ¿Es la carpeta del proyecto? (la crea scripts/preparar.py)")
    plan = json.load(open(plan_ruta, encoding="utf-8"))
    frases_pal = [palabras_frase(f["texto"]) for f in plan["frases"]]
    if any(len(fp) == 0 for fp in frases_pal):
        sys.exit("Hay frases sin texto en el plan")
    salida_t = os.path.join(proy, "src", "datos", "tiempos.json")

    if a.sin_voz:
        t, frases = 0.35, []
        seg_sil = 60 / a.ppm / 2.1  # ~2,1 sílabas por palabra en español
        for fp in frases_pal:
            ini = t
            pals = []
            for w, c, g in fp:
                pals.append({"w": w, "t": round(t, 3), "clave": c, "g": g})
                t += max(0.16, silabas(w) * seg_sil) + (0.16 if re.search(r"[,;:]$", w) else 0)
            frases.append({"texto": " ".join(w for w, _, _ in fp), "inicio": round(ini, 3), "fin": round(t, 3), "palabras": pals})
            t += 0.35
        dur = t + a.cola
        json.dump({"voz": None, "motor": "sin-voz", "duracion": round(dur, 3), "frases": frases}, open(salida_t, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"sin voz: {dur:.1f} s a {a.ppm:.0f} palabras/min → {salida_t}")
        return

    if not a.audio:
        sys.exit("Falta el archivo de audio (o usa --sin-voz)")
    x = decodificar(proy, a.audio, a.tempo)
    bruto = len(x) / SR
    x = acortar_pausas(x, a.pausa)
    habla = len(x) / SR

    modelo = ruta_modelo()
    motor = a.motor
    if motor == "auto":
        try:
            import sherpa_onnx  # type: ignore  # noqa: F401

            motor = "asr" if modelo else "silabas"
        except Exception:
            motor = "silabas"
    if motor == "asr" and not modelo:
        sys.exit(f"Para --motor asr hace falta el modelo Parakeet v3 (~470 MB de descarga): descárgalo de {MODELO_URL}, descomprímelo en ~/.cache/becario-reels/ e instala sherpa-onnx (pip install sherpa-onnx). O usa --motor silabas.")

    info, asr = None, []
    if motor == "asr":
        B, E, ts, info, asr = tiempos_por_asr(x, frases_pal, modelo)
    else:
        B, E, ts = tiempos_por_silabas(x, frases_pal)
    sil_frase = [sum(silabas(w) for w, _, _ in fp) for fp in frases_pal]
    avisos = avisos_ritmo(B, E, sil_frase, [" ".join(w for w, _, _ in fp) for fp in frases_pal])

    # audio final: paso alto, cola de silencio y normalizado a -14 LUFS (como los reels de referencia)
    x = paso_alto(x)
    x = np.concatenate([x, np.zeros(int(a.cola * SR), dtype=np.float32)])
    total = len(x) / SR
    os.makedirs(os.path.join(proy, "public"), exist_ok=True)
    voz = os.path.join(proy, "public", "voz.wav")
    tmp = voz + ".tmp.wav"
    guardar_wav(tmp, x)
    ff(proy, ["-y", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=7", "-ar", str(SR), "-ac", "1", voz])
    os.remove(tmp)

    frases = []
    for i, fp in enumerate(frases_pal):
        ini = B[i] if i < len(B) else ts[i][0]
        fin = E[i] if i < len(E) else ts[i][-1] + 0.3
        if frases and ini <= frases[-1]["fin"]:
            ini = frases[-1]["fin"] + 0.01
        fin = max(fin, ts[i][-1] + 0.1)
        frases.append({"texto": " ".join(w for w, _, _ in fp), "inicio": round(ini, 3), "fin": round(fin, 3), "palabras": [{"w": w, "t": round(max(t, ini), 3), "clave": c, "g": g} for (w, c, g), t in zip(fp, ts[i])]})
    json.dump({"voz": os.path.basename(a.audio), "motor": motor, "velocidad": a.tempo, "duracion": round(total, 3), "frases": frases}, open(salida_t, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    n = sum(len(fp) for fp in frases_pal)
    print(f"audio: {bruto:.2f} s → {habla:.2f} s de voz tras recortar pausas (+{a.cola} s de cola) = {total:.2f} s")
    print(f"motor: {motor} · {n} palabras · {n / habla * 60:.0f} palabras/min" + (f" · reconocidas {info['oidas']}/{n}, usadas en su frase {info['usadas']}/{n}" if info else ""))
    if n / habla * 60 < 185:
        print("  (va algo lenta para un reel: prueba --tempo 1.05)")
    for f in frases:
        print(f"{f['inicio']:6.2f}-{f['fin']:6.2f}  {f['texto']}")
    for av in avisos:
        print(av)
    print(f"→ {voz}\n→ {salida_t}")


if __name__ == "__main__":
    main()
