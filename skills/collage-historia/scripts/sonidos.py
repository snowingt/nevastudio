"""Efectos de sonido sintetizados (sin archivos ni licencias de terceros)."""
import numpy as np

SR = 48000


def _env(n, ataque=0.003, caida=8.0):
    t = np.arange(n) / SR
    a = np.minimum(1, t / max(1e-4, ataque))
    return a * np.exp(-t * caida)


def _tono(f0, f1, dur, caida=10.0, forma="seno"):
    n = int(SR * dur)
    f = np.linspace(f0, f1, n)
    fase = 2 * np.pi * np.cumsum(f) / SR
    w = np.sin(fase) if forma == "seno" else np.sign(np.sin(fase)) * 0.5
    return w * _env(n, caida=caida)


def _ruido(dur, caida=30.0, agudo=True, rng=None):
    rng = rng or np.random.default_rng(1)
    n = int(SR * dur)
    r = rng.standard_normal(n)
    if agudo:
        r = np.diff(np.concatenate([[0], r]))
    else:
        r = np.convolve(r, np.ones(24) / 24, mode="same")
    return r * _env(n, ataque=0.001, caida=caida)


def _suma(*partes):
    n = max(len(p) for p in partes)
    out = np.zeros(n)
    for p in partes:
        out[:len(p)] += p
    return out


def efecto(nombre, rng):
    if nombre == "pop":  # blip de 8 bits
        f = rng.uniform(620, 760)
        return 0.13 * _suma(_tono(f, f * 1.5, 0.07, caida=30, forma="cuadrada"), 0.5 * _tono(f * 2, f * 2, 0.03, caida=80, forma="cuadrada"))
    if nombre == "moneda":
        a = _tono(988, 988, 0.07, caida=6, forma="cuadrada")
        b = _tono(1319, 1319, 0.28, caida=9, forma="cuadrada")
        return 0.12 * np.concatenate([a, b])
    if nombre == "nivel":
        out = []
        for f in [523, 659, 784, 1047, 1319]:
            out.append(_tono(f, f, 0.085, caida=3, forma="cuadrada"))
        out.append(_tono(1568, 1568, 0.35, caida=6, forma="cuadrada"))
        return 0.11 * np.concatenate(out)
    if nombre == "blip":
        return 0.12 * _suma(_tono(1200, 1800, 0.06, caida=20, forma="cuadrada"))
    if nombre == "golpe":
        return _suma(0.35 * _tono(140, 50, 0.22, caida=14), 0.12 * _ruido(0.08, 40, agudo=False, rng=rng))
    if nombre == "tecla":
        return _suma(0.09 * _ruido(0.018, caida=220, rng=rng), 0.04 * _tono(rng.uniform(1800, 2600), 1500, 0.015, caida=260))
    if nombre == "check":
        return 0.16 * _suma(_tono(1046, 1046, 0.22, caida=14), 0.6 * np.pad(_tono(1568, 1568, 0.2, caida=14), (int(SR * 0.05), 0)))
    if nombre == "exito":
        out = np.zeros(int(SR * 0.6))
        for i, f in enumerate([784, 988, 1175, 1568]):
            s = _tono(f, f, 0.3, caida=9) * 0.15
            k = int(SR * 0.07 * i)
            out[k:k + len(s)] += s[:len(out) - k]
        return out
    if nombre == "barra":
        return 0.07 * _tono(300, 760, 0.45, caida=3)
    if nombre == "clic":
        return _suma(0.28 * _ruido(0.006, caida=500, rng=rng), 0.12 * _tono(2200, 1800, 0.025, caida=150))
    if nombre == "pasa":
        n = int(SR * 0.28)
        r = np.convolve(rng.standard_normal(n), np.ones(12) / 12, mode="same")
        env = np.sin(np.linspace(0, np.pi, n)) ** 2
        return 0.11 * r * env
    if nombre == "tic":
        return 0.2 * _tono(1500, 1400, 0.035, caida=120)
    if nombre == "tachar":
        return 0.12 * _tono(420, 220, 0.18, caida=10, forma="cuadrada")
    if nombre == "rec":
        return 0.13 * _tono(1000, 1000, 0.12, caida=6)
    return np.zeros(10)


def pista(eventos, duracion, ganancia=1.0, semilla=7):
    """eventos: lista de (segundo, nombre). Devuelve la pista mono float32 a 48 kHz."""
    rng = np.random.default_rng(semilla)
    out = np.zeros(int(SR * (duracion + 1.0)), np.float32)
    ultimos = {}
    for t, nombre in sorted(eventos):
        if nombre != "tecla" and t - ultimos.get("_cualquiera", -1) < 0.045:
            continue
        if nombre == "tecla" and t - ultimos.get("tecla", -1) < 0.05:
            continue
        ultimos[nombre] = t
        if nombre != "tecla":
            ultimos["_cualquiera"] = t
        s = efecto(nombre, rng).astype(np.float32) * ganancia
        k = int(t * SR)
        if k < 0 or k >= len(out):
            continue
        fin = min(len(out), k + len(s))
        out[k:fin] += s[:fin - k]
    return out[:int(SR * duracion)]
