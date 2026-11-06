#!/usr/bin/env python3
"""Comprueba que el ordenador tiene lo necesario y lo instala si falta.

Uso:  python3 comprobar.py
"""
import importlib, os, subprocess, sys

ok = True


def instala(paquete):
    for extra in (["--break-system-packages"], [], ["--user", "--break-system-packages"], ["--user"]):
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *extra, paquete], capture_output=True, text=True)
        if r.returncode == 0:
            return True
    return False


print(f"Python {sys.version.split()[0]}")
if sys.version_info < (3, 9):
    print("  ✗ Hace falta Python 3.9 o más nuevo."); ok = False
for mod, pkg in (("PIL", "pillow"), ("numpy", "numpy")):
    try:
        m = importlib.import_module(mod)
        print(f"  ✓ {pkg} {getattr(m, '__version__', '')}")
    except ImportError:
        print(f"  … instalando {pkg}")
        if not instala(pkg):
            print(f"  ✗ No se pudo instalar {pkg}."); ok = False
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from comun import FFMPEG, fuente
    r = subprocess.run([FFMPEG, "-version"], capture_output=True, text=True)
    print("  ✓ ffmpeg:", r.stdout.split("\n")[0][:60])
    tiene_x264 = "libx264" in subprocess.run([FFMPEG, "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    print("  ✓ codificador H.264" if tiene_x264 else "  ✗ ffmpeg sin libx264"); ok = ok and tiene_x264
    for f in ("black", "bold", "semi", "cursiva"):
        fuente(f, 40)
    print("  ✓ fuentes Poppins y Lora")
except SystemExit as e:
    print("  ✗", e); ok = False
try:
    import faster_whisper  # noqa: F401
    print("  ✓ faster-whisper (reconocimiento de voz)")
except ImportError:
    print("  · faster-whisper no está: alinear.py lo instalará si hay voz (sin voz no hace falta).")


def sin_permiso(raiz):
    """Carpetas y archivos de la copia en los que no se puede escribir (cp -r conserva el solo lectura)."""
    malos = [raiz] if not os.access(raiz, os.W_OK) else []
    for d, carpetas, archivos in os.walk(raiz):
        for n in carpetas + archivos:
            ruta = os.path.join(d, n)
            if not os.path.islink(ruta) and not os.access(ruta, os.W_OK):
                malos.append(ruta)
    return malos


raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
malos = sin_permiso(raiz)
if malos:
    subprocess.run(["chmod", "-R", "u+w", raiz], capture_output=True)
    if sin_permiso(raiz):
        print(f"  ✗ No se puede escribir en {raiz}. Parece la carpeta de la skill, que es de solo lectura:"
              " cópiala con el comando de SKILL.md y trabaja en la copia."); ok = False
    else:
        print(f"  ✓ permisos de escritura arreglados ({len(malos)} carpetas o archivos eran de solo lectura)")
else:
    print("  ✓ la carpeta de trabajo se puede escribir")
print("TODO LISTO" if ok else "FALTA ALGO: mira los ✗ de arriba.")
sys.exit(0 if ok else 1)
