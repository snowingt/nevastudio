"""Prepara las poses del personaje (opcional) y guarda sus medidas en src/datos/poses.json.

Uso (desde cualquier carpeta):
  python3 poses.py --proyecto ~/reel recortar normal foto_normal.png    quita el fondo liso, recorta y añade la pose "normal"
  python3 poses.py --proyecto ~/reel recortar celebra celebra.png piensa piensa.jpg     …varias de una vez
  python3 poses.py --proyecto ~/reel recortar carpeta_con_poses/        todas las imágenes de una carpeta (nombre = archivo)
  python3 poses.py --proyecto ~/reel medir                              vuelve a medir todo lo que hay en public/personaje
  python3 poses.py --proyecto ~/reel ajustar celebra anchoCabeza=380    corrige a mano una medida que haya salido mal
  python3 poses.py --proyecto ~/reel quitar celebra                     borra una pose

Para que el personaje no "salte" al cambiar de pose, el vídeo coloca todas las poses con la cabeza del mismo
tamaño y en el mismo sitio. Por eso se mide la cabeza de cada imagen:
  cabeza       x del centro de la cabeza (0–1 del ancho de la imagen)
  anchoCabeza  ancho de la cabeza en píxeles
  peloArriba   y de lo más alto de la cabeza en píxeles
La cabeza se busca por su color: el color dominante de lo alto de la pose de referencia (la que se llame
"normal", o la primera que añadas). Elige como referencia una pose tranquila, sin los brazos por encima de la
cabeza. Si una medida sale mal, mírala en la hoja de contacto y corrígela con «ajustar».

Imágenes: PNG con fondo transparente, o con fondo liso de un color (se quita solo). Personaje de cintura para
arriba, mirando a cámara, todas con el mismo dibujo y la misma escala aproximada.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

REFERENCIAS = ("normal", "neutral", "base", "habla", "presenta")


def rutas(proyecto):
    if not os.path.exists(os.path.join(proyecto, "src", "datos", "plan.json")):
        print(f"AVISO: {proyecto} no parece la carpeta de un reel (falta src/datos/plan.json). ¿Has ejecutado preparar.py?")
    d = os.path.join(proyecto, "public", "personaje")
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(proyecto, "src", "datos"), exist_ok=True)
    return d, os.path.join(proyecto, "src", "datos", "poses.json")


# ------------------------------------------------------------------ recorte

def componentes(mascara):
    """Etiqueta componentes conexos (4-vecinos) sin depender de OpenCV."""
    try:
        from scipy import ndimage

        lab, n = ndimage.label(mascara)
        return lab, n
    except ImportError:  # pragma: no cover
        raise SystemExit("Falta scipy: pip install scipy --break-system-packages")


def fondo_de(img):
    h, w, _ = img.shape
    k = max(8, min(h, w) // 40)
    esquinas = np.concatenate([img[:k, :k].reshape(-1, 3), img[:k, -k:].reshape(-1, 3), img[-k:, :k].reshape(-1, 3), img[-k:, -k:].reshape(-1, 3)])
    return np.median(esquinas, axis=0)


def quitar_fondo(img, tol=26, banda=3.0):
    """Quita un fondo liso con borde fino: alfa suave en el contorno y el color del borde limpio de restos del fondo
    (si no, sobre un fondo distinto al original sale un halo claro o "de recortado" alrededor de la figura)."""
    from scipy import ndimage

    img = img.astype(float)
    B = fondo_de(img)
    d = np.abs(img - B).max(axis=2)
    cerca = d < tol
    ratio = img / np.maximum(B, 1)
    sombra = (ratio.min(axis=2) > 0.70) & (ratio.max(axis=2) < 0.985) & ((ratio.max(axis=2) - ratio.min(axis=2)) < 0.06)
    lab, n = componentes(cerca | sombra)
    semillas = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fondo = np.isin(lab, list(semillas))
    # huecos cerrados del color del fondo (entre brazo y cuerpo, entre dedos)
    areas = np.bincount(lab.ravel(), minlength=n + 1)
    for k in range(1, n + 1):
        if k not in semillas and areas[k] > 400:
            comp = lab == k
            if (d[comp] < tol * 0.6).mean() > 0.85:
                fondo |= comp
    figura = ~fondo
    # restos sueltos
    lab2, n2 = componentes(figura)
    if n2 > 1:
        ar = np.bincount(lab2.ravel(), minlength=n2 + 1)[1:]
        grande = 1 + int(np.argmax(ar))
        for k in range(1, n2 + 1):
            if k != grande and ar[k - 1] < 0.004 * figura.size:
                figura[lab2 == k] = False
    # borde: para cada píxel cerca del contorno, el color "limpio" es el del píxel de dentro más cercano
    # y el alfa sale de cuánto se parece al fondo frente a ese color
    dentro = ndimage.distance_transform_edt(figura)
    fuera = ndimage.distance_transform_edt(~figura)
    solido = dentro > banda
    if not solido.any():
        solido = figura
    _, (iy, ix) = ndimage.distance_transform_edt(~solido, return_indices=True)
    F = img[iy, ix]
    zona = ((dentro <= banda) & figura) | ((fuera <= 2.0) & ~figura)
    FB = F - B
    num = ((img - B) * FB).sum(axis=2)
    den = (FB * FB).sum(axis=2)
    fiable = den > 60.0 ** 2
    alpha = figura.astype(float)
    usar = zona & fiable
    alpha[usar] = np.clip(num / np.maximum(den, 1e-6), 0, 1)[usar]
    alpha[solido] = 1.0
    out = img.copy()
    borde = usar & (alpha < 0.999)
    out[borde] = F[borde]
    alpha = ndimage.gaussian_filter(alpha, 0.5)
    alpha[solido] = 1.0
    rgba = np.dstack([np.clip(out, 0, 255), np.clip(alpha * 255, 0, 255)]).astype(np.uint8)
    return rgba, B


def recortar(src):
    im = Image.open(src)
    rgba = np.asarray(im.convert("RGBA")).copy()
    transparente = (rgba[..., 3] < 250).mean() > 0.02
    bg = None
    if not transparente:
        rgba, bg = quitar_fondo(rgba[..., :3])
    ys, xs = np.where(rgba[..., 3] > 10)
    if len(xs) == 0:
        raise SystemExit(f"{src}: no encuentro ninguna figura (¿la imagen está vacía o es todo fondo?)")
    return rgba[ys.min(): ys.max() + 1, xs.min(): xs.max() + 1], bg


def alargar_si_cortado(rgba, px=90):
    """Si la figura llega cortada al borde inferior, repite la última fila para que al animarla nunca se vea el corte."""
    ultima = rgba[-1:, :, :]
    if (ultima[..., 3] > 200).mean() < 0.15:
        return rgba, False
    if len(rgba) > 30 and (rgba[-30:] == ultima).all():
        return rgba, False
    return np.concatenate([rgba, np.repeat(ultima, px, axis=0)], axis=0), True


# ------------------------------------------------------------------ medidas

def color_cabeza(rgba):
    """Color dominante de lo más alto de la figura (pelo, gorro o la propia cabeza)."""
    a = rgba[..., 3] > 200
    ys, xs = np.where(a)
    y0, y1 = ys.min(), ys.max()
    alto = y1 - y0
    franja = a & (np.arange(rgba.shape[0])[:, None] <= y0 + 0.10 * alto)
    px = rgba[..., :3][franja].astype(float)
    if len(px) < 50:
        px = rgba[..., :3][a].astype(float)
    rng = np.random.default_rng(0)
    if len(px) > 20000:
        px = px[rng.choice(len(px), size=20000, replace=False)]
    # k-medias simple (k=3) y nos quedamos con el grupo más grande
    centros = px[rng.choice(len(px), size=min(3, len(px)), replace=False)]
    for _ in range(12):
        g = ((px[:, None, :] - centros[None]) ** 2).sum(-1).argmin(1)
        centros = np.array([px[g == k].mean(0) if (g == k).any() else centros[k] for k in range(len(centros))])
    g = ((px[:, None, :] - centros[None]) ** 2).sum(-1).argmin(1)
    return centros[np.bincount(g).argmax()]


def medir(nombre, rgba, color, tol=30.0):
    from scipy import ndimage

    h, w = rgba.shape[:2]
    a = rgba[..., 3] > 200
    ys_all = np.where(a.any(axis=1))[0]
    y0, y1 = ys_all.min(), ys_all.max()
    dist = np.sqrt(((rgba[..., :3].astype(float) - color) ** 2).sum(-1))
    aviso = None
    for t in (tol, tol * 1.5, tol * 2.2):
        m = a & (dist < t)
        m = ndimage.binary_opening(m, structure=np.ones((3, 3)))
        lab, n = componentes(m)
        if n == 0:
            continue
        areas = np.bincount(lab.ravel(), minlength=n + 1)
        cajas = ndimage.find_objects(lab)
        # la cabeza es la mancha de ese color que está más arriba (con un tamaño mínimo)
        mejor = None
        for k, caja in enumerate(cajas, start=1):
            if caja is None or areas[k] < 0.002 * a.sum():
                continue
            arriba_k = caja[0].start
            if arriba_k > y0 + 0.45 * (y1 - y0):
                continue
            if mejor is None or arriba_k < mejor[1] - 4:
                mejor = (k, arriba_k)
        if mejor is not None:
            k = mejor[0]
            caja = cajas[k - 1]
            sub = lab[caja] == k
            yy, xx = np.where(sub)
            yy = yy + caja[0].start
            xx = xx + caja[1].start
            arriba = np.percentile(yy, 0.3)
            corte = arriba + 0.55 * (np.percentile(yy, 99) - arriba)
            sel = yy <= corte
            x6, x50, x94 = np.percentile(xx[sel], [6, 50, 94])
            if x94 - x6 > 0.08 * w:
                return {"src": f"personaje/{nombre}.png", "ancho": int(w), "alto": int(h), "cabeza": round(float(x50 / w), 4), "anchoCabeza": round(float(x94 - x6), 1), "peloArriba": round(float(arriba), 1)}, aviso
        aviso = "no encuentro bien la cabeza por su color; uso la silueta"
    # plan B: lo más alto de la silueta
    fila = int(y0 + 0.10 * (y1 - y0))
    xs = np.where(a[fila])[0]
    ancho = float(xs.max() - xs.min()) if len(xs) else 0.3 * w
    cx = float(xs.mean() / w) if len(xs) else 0.5
    return {"src": f"personaje/{nombre}.png", "ancho": int(w), "alto": int(h), "cabeza": round(cx, 4), "anchoCabeza": round(ancho, 1), "peloArriba": float(y0)}, "no encuentro la cabeza; uso lo más alto de la silueta (revísalo)"


# ------------------------------------------------------------------ comandos

def cargar(ruta):
    return json.load(open(ruta)) if os.path.exists(ruta) else {}


def guardar(ruta, datos):
    meta = {k: v for k, v in datos.items() if k.startswith("_")}
    poses = {k: datos[k] for k in sorted(datos) if not k.startswith("_")}
    json.dump({**meta, **poses}, open(ruta, "w"), indent=1, ensure_ascii=False)


def referencia(dir_poses, datos, pedida=None):
    nombres = sorted(f[:-4] for f in os.listdir(dir_poses) if f.endswith(".png"))
    if pedida:
        return pedida
    if datos.get("_referencia") in nombres:
        return datos["_referencia"]
    for r in REFERENCIAS:
        if r in nombres:
            return r
    return nombres[0] if nombres else None


def medir_todo(dir_poses, ruta, pedida=None):
    datos = cargar(ruta)
    ref = referencia(dir_poses, datos, pedida)
    if not ref:
        print("No hay poses en public/personaje.")
        return
    rgba_ref = np.asarray(Image.open(os.path.join(dir_poses, f"{ref}.png")).convert("RGBA"))
    color = color_cabeza(rgba_ref)
    ajustes = datos.get("_ajustes", {})
    nuevos = {"_referencia": ref, "_colorCabeza": "#%02X%02X%02X" % tuple(int(v) for v in color), "_ajustes": ajustes}
    for f in sorted(os.listdir(dir_poses)):
        if not f.endswith(".png"):
            continue
        n = f[:-4]
        rgba = np.asarray(Image.open(os.path.join(dir_poses, f)).convert("RGBA"))
        rgba2, alargado = alargar_si_cortado(rgba)
        if alargado:
            Image.fromarray(rgba2, "RGBA").save(os.path.join(dir_poses, f), optimize=True)
            print(f"{n}: alargada por abajo (llegaba cortada)")
        m, aviso = medir(n, rgba2, color)
        m.update(ajustes.get(n, {}))
        nuevos[n] = m
        print(f"{n:16s} cabeza x={m['cabeza']:.3f}  ancho={m['anchoCabeza']:.0f}px  arriba={m['peloArriba']:.0f}px" + (f"   AVISO: {aviso}" if aviso else ""))
    guardar(ruta, nuevos)
    print(f"referencia: «{ref}» (color de la cabeza {nuevos['_colorCabeza']}). Medidas en src/datos/poses.json")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proyecto", default=".")
    ap.add_argument("--referencia", help="pose que se usa para saber el color de la cabeza")
    ap.add_argument("accion", choices=["recortar", "medir", "ajustar", "quitar"])
    ap.add_argument("resto", nargs="*")
    a = ap.parse_args()
    proyecto = os.path.abspath(os.path.expanduser(a.proyecto))
    dir_poses, ruta = rutas(proyecto)
    if a.accion == "recortar":
        # recortar nombre imagen [nombre imagen …]   o   recortar carpeta/  (usa el nombre de cada archivo)
        pares = []
        if len(a.resto) == 1 and os.path.isdir(os.path.expanduser(a.resto[0])):
            d = os.path.expanduser(a.resto[0])
            for f in sorted(os.listdir(d)):
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    base = os.path.splitext(f)[0].lower()
                    nombre = "".join(c if c.isalnum() else "_" for c in base).strip("_")
                    pares.append((nombre, os.path.join(d, f)))
        elif len(a.resto) >= 2 and len(a.resto) % 2 == 0:
            pares = [(a.resto[k], os.path.expanduser(a.resto[k + 1])) for k in range(0, len(a.resto), 2)]
        else:
            sys.exit("Uso: poses.py recortar <nombre> <imagen> [<nombre> <imagen> …]   o   poses.py recortar <carpeta>")
        for nombre, src in pares:
            if not nombre.replace("_", "").isalnum():
                sys.exit(f"«{nombre}»: el nombre de la pose solo puede tener letras, números y _ (ej.: senala_arriba)")
            out, bg = recortar(src)
            out, _ = alargar_si_cortado(out)
            Image.fromarray(out, "RGBA").save(os.path.join(dir_poses, f"{nombre}.png"), optimize=True)
            print(f"{nombre}: {'fondo transparente' if bg is None else 'fondo #%02X%02X%02X quitado' % tuple(int(v) for v in bg)} · {out.shape[1]}×{out.shape[0]}")
        medir_todo(dir_poses, ruta, a.referencia)
    elif a.accion == "medir":
        medir_todo(dir_poses, ruta, a.referencia)
    elif a.accion == "ajustar":
        if len(a.resto) < 2:
            sys.exit("Uso: poses.py ajustar <nombre> clave=valor [clave=valor …]  (claves: cabeza, anchoCabeza, peloArriba)")
        datos = cargar(ruta)
        nombre = a.resto[0]
        aj = datos.setdefault("_ajustes", {}).setdefault(nombre, {})
        for kv in a.resto[1:]:
            k, v = kv.split("=", 1)
            if k not in ("cabeza", "anchoCabeza", "peloArriba"):
                sys.exit(f"Clave desconocida: {k}")
            aj[k] = float(v)
            if nombre in datos:
                datos[nombre][k] = float(v)
        guardar(ruta, datos)
        print(f"{nombre}: {aj}")
    elif a.accion == "quitar":
        datos = cargar(ruta)
        for n in a.resto:
            datos.pop(n, None)
            datos.get("_ajustes", {}).pop(n, None)
            p = os.path.join(dir_poses, f"{n}.png")
            if os.path.exists(p):
                os.remove(p)
            print(f"{n}: quitada")
        guardar(ruta, datos)


if __name__ == "__main__":
    main()
