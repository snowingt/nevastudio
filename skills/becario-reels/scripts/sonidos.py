"""Genera la biblioteca de efectos de sonido de la plantilla (síntesis pura, sin muestras de terceros).

Uso:
  python3 sonidos.py <carpeta_salida>

Crea WAV mono de 48 kHz, normalizados a -1 dBFS de pico. Todos son deterministas (misma semilla),
así que volver a generarlos da exactamente los mismos archivos. No hace falta ejecutarlo: la plantilla
ya trae los WAV. Sirve para retocar un sonido o crear variantes.
"""
import os
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
RNG = np.random.default_rng(7)


def t_(dur):
    return np.arange(int(dur * SR)) / SR


def banda(x, lo, hi, orden=2):
    sos = butter(orden, [lo, hi], btype="bandpass", fs=SR, output="sos")
    return sosfilt(sos, x)


def paso_bajo(x, fc, orden=2):
    return sosfilt(butter(orden, fc, btype="lowpass", fs=SR, output="sos"), x)


def paso_alto(x, fc, orden=2):
    return sosfilt(butter(orden, fc, btype="highpass", fs=SR, output="sos"), x)


def barrido(ruido, f0, f1, ancho=0.6, trozo=256):
    """Filtro paso banda cuyo centro va de f0 a f1 (exponencial), aplicado por bloques con solape."""
    n = len(ruido)
    out = np.zeros(n)
    win = np.hanning(trozo * 2)
    for i in range(0, n, trozo):
        a, b = max(0, i - trozo), min(n, i + trozo)
        p = i / n
        fc = f0 * (f1 / f0) ** p
        lo, hi = fc * (1 - ancho / 2), min(fc * (1 + ancho / 2), SR / 2 - 100)
        seg = banda(ruido[a:b], max(lo, 30), hi)
        w = win[: b - a] if b - a == len(win) else np.hanning(b - a)
        out[a:b] += seg * w
    return out


def seno(f, t):
    """Seno con frecuencia variable (array) o fija."""
    if np.isscalar(f):
        return np.sin(2 * np.pi * f * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def guardar(carpeta, nombre, x, pico_db=-1.0):
    x = np.asarray(x, dtype=np.float64)
    fade = int(0.004 * SR)
    x[-fade:] *= np.linspace(1, 0, fade)
    x[: int(0.0008 * SR)] *= np.linspace(0, 1, int(0.0008 * SR))
    x = x / (np.abs(x).max() + 1e-12) * 10 ** (pico_db / 20)
    with wave.open(os.path.join(carpeta, nombre + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


# ------------------------------------------------------------------ sonidos

def pop():
    t = t_(0.14)
    f = 170 + 560 * np.exp(-t * 48)
    x = seno(f, t) * np.exp(-t * 34)
    x += 0.35 * paso_alto(RNG.standard_normal(len(t)), 2000) * np.exp(-t * 500)
    return x


def ding(f0=1318.5, dur=1.3, brillo=1.0):
    t = t_(dur)
    parciales = [(1.0, 1.0, 3.2), (2.0, 0.28, 4.6), (2.76, 0.42 * brillo, 6.0), (5.40, 0.20 * brillo, 9.0), (8.93, 0.10 * brillo, 13.0)]
    x = sum(a * np.sin(2 * np.pi * f0 * r * t + r) * np.exp(-t * d) for r, a, d in parciales)
    return x * (1 - np.exp(-t * 900))


def exito():
    a = ding(1318.5, 0.9)
    b = ding(1975.5, 1.1)
    x = np.zeros(int(1.25 * SR))
    x[: len(a)] += a
    o = int(0.085 * SR)
    x[o : o + len(b)] += 0.9 * b[: len(x) - o]
    return x


def campana():
    t = t_(1.8)
    x = np.zeros_like(t)
    for f, a, d in [(880, 1.0, 2.2), (882.5, 0.6, 2.4), (1760, 0.3, 3.5), (2423, 0.25, 4.5), (3520, 0.12, 6)]:
        x += a * np.sin(2 * np.pi * f * t) * np.exp(-t * d)
    return x * (1 - np.exp(-t * 300))


def tecla():
    t = t_(0.06)
    clic = banda(RNG.standard_normal(len(t)), 1800, 7000) * np.exp(-t * 260)
    golpe = np.sin(2 * np.pi * 320 * t) * np.exp(-t * 120) * 0.5
    return clic + golpe


def tic():
    t = t_(0.03)
    return np.sin(2 * np.pi * 2300 * t) * np.exp(-t * 220)


def clic():
    t = t_(0.012)
    return paso_alto(RNG.standard_normal(len(t)), 3000) * np.exp(-t * 900)


def whoosh(dur=0.5, f0=350, f1=2600):
    t = t_(dur)
    p = t / dur
    env = np.sin(np.pi * np.clip(p, 0, 1) ** 0.75) ** 2
    x = barrido(RNG.standard_normal(len(t)), f0, f1, ancho=0.9) * env
    return x


def swoosh():
    return whoosh(0.28, 900, 5200)


def papel():
    t = t_(0.09)
    return banda(RNG.standard_normal(len(t)), 900, 5000) * np.exp(-t * 60) * (1 - np.exp(-t * 2000))


def burbuja():
    x = np.zeros(int(0.32 * SR))
    for k, (ini, f0, f1, dur) in enumerate([(0.0, 260, 1100, 0.07), (0.11, 380, 1500, 0.06), (0.19, 300, 1250, 0.07)]):
        t = t_(dur)
        f = f0 + (f1 - f0) * (t / dur) ** 1.5
        b = seno(f, t) * np.sin(np.pi * t / dur) ** 2 * (0.9 - 0.2 * k)
        o = int(ini * SR)
        x[o : o + len(b)] += b
    return x


def golpe():
    t = t_(0.32)
    f = 42 + 80 * np.exp(-t * 28)
    x = seno(f, t) * np.exp(-t * 9)
    x += 0.4 * paso_bajo(RNG.standard_normal(len(t)), 1200) * np.exp(-t * 60)
    return x


def negacion():
    x = np.zeros(int(0.32 * SR))
    for ini, f in [(0.0, 233), (0.15, 185)]:
        t = t_(0.12)
        onda = np.tanh(3 * np.sin(2 * np.pi * f * t)) * 0.8 + 0.2 * np.sin(4 * np.pi * f * t)
        b = paso_bajo(onda, 2200) * np.sin(np.pi * np.clip(t / 0.12, 0, 1)) ** 0.5
        o = int(ini * SR)
        x[o : o + len(b)] += b
    return x


def puff():
    t = t_(0.35)
    return paso_bajo(RNG.standard_normal(len(t)), 1400) * np.exp(-t * 14) * (1 - np.exp(-t * 400))


def cristal():
    t = t_(0.9)
    x = paso_alto(RNG.standard_normal(len(t)), 2500) * np.exp(-t * 30) * 0.6
    for k in range(10):
        f = 2600 + RNG.random() * 6400
        ini = RNG.random() * 0.25
        tt = np.clip(t - ini, 0, None)
        x += (t >= ini) * np.sin(2 * np.pi * f * tt) * np.exp(-tt * (12 + RNG.random() * 18)) * (0.25 + RNG.random() * 0.3)
    return x


def proyector():
    """Traqueteo de proyector de cine: clics regulares a 18 por segundo con un zumbido suave."""
    t = t_(1.0)
    x = 0.08 * np.sin(2 * np.pi * 110 * t)
    for k in range(18):
        o = int(k / 18 * SR)
        c = clic() * 0.8
        x[o : o + len(c)] += c[: len(x) - o]
    return x * np.minimum(1, (1 - t) * 6)


def subida():
    t = t_(0.9)
    x = barrido(RNG.standard_normal(len(t)), 200, 4000, ancho=0.7) * (t / 0.9) ** 2
    x += 0.3 * seno(220 * (1 + 3 * (t / 0.9) ** 2), t) * (t / 0.9) ** 2
    return x


SONIDOS = {
    "pop": pop, "ding": ding, "exito": exito, "campana": campana, "tecla": tecla, "tic": tic, "clic": clic,
    "whoosh": whoosh, "swoosh": swoosh, "papel": papel, "burbuja": burbuja, "golpe": golpe, "negacion": negacion,
    "puff": puff, "cristal": cristal, "proyector": proyector, "subida": subida,
}

if __name__ == "__main__":
    carpeta = sys.argv[1] if len(sys.argv) > 1 else "sonidos"
    os.makedirs(carpeta, exist_ok=True)
    for nombre, fn in SONIDOS.items():
        guardar(carpeta, nombre, fn())
    print(f"{len(SONIDOS)} sonidos en {carpeta}: {', '.join(SONIDOS)}")
