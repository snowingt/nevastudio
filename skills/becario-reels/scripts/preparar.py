"""Crea la carpeta de trabajo de un reel a partir de la plantilla y deja todo listo para renderizar.

Uso:
  python3 preparar.py ~/reel                 copia la plantilla, instala dependencias y busca navegador y ffmpeg
  python3 preparar.py ~/reel --actualizar    vuelve a copiar el motor sin tocar src/datos, public/ ni src/propias

Al terminar escribe entorno.json (navegador y ffmpeg encontrados) y comprueba que el render arranca.
Se puede volver a ejecutar sin miedo: lo que ya está hecho se salta.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
PLANTILLA = os.path.join(os.path.dirname(AQUI), "assets", "plantilla")


def run(cmd, cwd=None, timeout=900, env=None):
    t = time.time()
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or ""), time.time() - t


def copiar_plantilla(destino, actualizar):
    os.makedirs(destino, exist_ok=True)
    conservar = {os.path.join("src", "datos"), os.path.join("src", "propias"), "public"} if actualizar else set()
    for raiz, dirs, archivos in os.walk(PLANTILLA):
        rel = os.path.relpath(raiz, PLANTILLA)
        dirs[:] = [d for d in dirs if d not in ("node_modules", "salida")]
        if any(rel == c or rel.startswith(c + os.sep) for c in conservar) and os.path.exists(os.path.join(destino, rel)):
            continue
        os.makedirs(os.path.join(destino, rel), exist_ok=True)
        for a in archivos:
            dst = os.path.join(destino, rel, a)
            if actualizar or not os.path.exists(dst):
                if os.path.exists(dst):
                    os.chmod(dst, 0o644)
                # solo el contenido: la carpeta de la skill suele ser de solo lectura y el proyecto tiene que poder editarse
                shutil.copyfile(os.path.join(raiz, a), dst)
                os.chmod(dst, 0o644)


def instalar(destino):
    if os.path.exists(os.path.join(destino, "node_modules", "@remotion", "renderer")):
        print("dependencias: ya instaladas")
        return True
    if not shutil.which("npm"):
        print("ERROR: no hay npm/Node.js en este entorno. Instala Node 18+ (https://nodejs.org) y repite.")
        return False
    cmd = ["npm", "ci"] if os.path.exists(os.path.join(destino, "package-lock.json")) else ["npm", "install"]
    for intento in range(2):
        print(f"dependencias: {' '.join(cmd)} (1–2 minutos)…")
        code, out, dt = run(cmd + ["--no-audit", "--no-fund", "--loglevel=error"], cwd=destino)
        if code == 0:
            print(f"dependencias: instaladas en {dt:.0f} s")
            return True
        print(out[-1500:])
        cmd = ["npm", "install"]  # si el lockfile no encaja con esta plataforma, se instala sin él
    print("ERROR: no se pudieron instalar las dependencias. Mira el mensaje de arriba (¿hay acceso a registry.npmjs.org?).")
    return False


def es_ejecutable(p):
    return p and os.path.isfile(p) and os.access(p, os.X_OK)


def buscar_navegador(destino):
    """Chrome/Chromium ya instalado → navegador de Remotion → Chromium empaquetado en npm (@sparticuz/chromium)."""
    candidatos = []
    for patron in [
        "/opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell",
        os.path.expanduser("~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell"),
        os.path.join(destino, "node_modules", ".remotion", "chrome-headless-shell", "*", "chrome-headless-shell-*", "chrome-headless-shell"),
        "/opt/pw-browsers/chromium-*/chrome-linux*/chrome",
        os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome"),
    ]:
        candidatos += sorted(glob.glob(patron), reverse=True)
    for b in ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome"]:
        w = shutil.which(b)
        if w:
            candidatos.append(w)
    if sys.platform == "darwin":
        candidatos.append("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if os.environ.get("BECARIO_SIN_NAVEGADOR_LOCAL"):  # solo para probar el plan B
        candidatos = []
    for c in candidatos:
        if es_ejecutable(c):
            modo = "headless-shell" if "headless" in os.path.basename(c) or "headless_shell" in c else "chrome-for-testing"
            return c, modo, "encontrado"
    # 1) que Remotion descargue su navegador (necesita acceso a storage.googleapis.com)
    code, out, _ = run(["node", "-e", "require('@remotion/renderer').ensureBrowser().then(()=>console.log('ok')).catch(e=>{console.error(e.message);process.exit(1)})"], cwd=destino, timeout=600)
    if code == 0:
        for c in sorted(glob.glob(os.path.join(destino, "node_modules", ".remotion", "**", "chrome-headless-shell"), recursive=True)):
            if es_ejecutable(c):
                return c, "headless-shell", "descargado por Remotion"
        return None, "headless-shell", "descargado por Remotion (ruta interna)"
    # si la descarga falla deja un candado que luego estorba
    for candado in glob.glob(os.path.join(destino, "node_modules", ".remotion", "*", "download.lock")):
        try:
            os.remove(candado)
        except OSError:
            pass
    # 2) Chromium que viene dentro de un paquete de npm (vale aunque solo haya acceso a npm)
    print("navegador: probando el Chromium empaquetado en npm (@sparticuz/chromium)…")
    code, out, _ = run(["npm", "install", "--no-save", "--no-audit", "--no-fund", "--loglevel=error", "@sparticuz/chromium@138"], cwd=destino, timeout=600)
    if code == 0:
        code, out, _ = run(["node", "-e", "const c=require('@sparticuz/chromium');Promise.resolve((c.default||c).executablePath()).then(p=>console.log(p))"], cwd=destino, timeout=300)
        p = out.strip().splitlines()[-1] if out.strip() else ""
        if code == 0 and es_ejecutable(p):
            return p, "headless-shell", "Chromium de npm"
    return None, None, "no encontrado"


def buscar_ffmpeg(destino):
    if shutil.which("ffmpeg"):
        return shutil.which("ffmpeg")
    for c in glob.glob(os.path.join(destino, "node_modules", "@remotion", "compositor-*", "ffmpeg")):
        return c
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("destino")
    ap.add_argument("--actualizar", action="store_true")
    a = ap.parse_args()
    destino = os.path.abspath(os.path.expanduser(a.destino))
    t0 = time.time()
    copiar_plantilla(destino, a.actualizar)
    print(f"plantilla: {destino}")
    if not instalar(destino):
        sys.exit(1)
    nav, modo, como = buscar_navegador(destino)
    ffm = buscar_ffmpeg(destino)
    entorno = {"navegador": nav, "modo": modo, "ffmpeg": ffm}
    json.dump(entorno, open(os.path.join(destino, "entorno.json"), "w"), indent=1)
    print(f"navegador: {nav or '—'} ({como})")
    print(f"ffmpeg: {ffm or '—'}")
    if not nav and como != "descargado por Remotion (ruta interna)":
        print("ERROR: no hay navegador para renderizar. En Claude Code instala Google Chrome; en la app, revisa que el acceso a red permita npm.")
        sys.exit(1)
    code, out, dt = run(["node", "render.mjs", "resumen"], cwd=destino, timeout=600)
    if code not in (0, 1):
        print("\n".join(out.strip().splitlines()[-15:]))
        print("ERROR: el motor de vídeo no arranca. Mira el mensaje de arriba y references/problemas.md")
        sys.exit(1)
    print(f"prueba del motor de vídeo: OK ({dt:.0f} s)")
    print(f"LISTO en {time.time() - t0:.0f} s. Siguiente paso: escribe src/datos/plan.json y alinea la voz.")


if __name__ == "__main__":
    main()
