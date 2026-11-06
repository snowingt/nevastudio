import React from "react";
import { Img, spring, staticFile, useCurrentFrame } from "remotion";
import { POSES } from "./actual";
import { FPS } from "./constantes";

// Todas las poses se colocan con la cabeza del mismo tamaño y en el mismo sitio (medidas de scripts/poses.py),
// así el personaje no "salta" al cambiar de pose.
const CABEZA_ANCHO = 228; // px en pantalla
const CABEZA_X = 300; // centro de la cabeza
const PELO_Y = 1262; // punta del pelo

/** Movimiento tranquilo: respiración lenta, balanceo casi imperceptible y entrada suave al cambiar de pose. */
export const Personaje: React.FC<{ cambios: { desde: number; pose: string }[] }> = ({ cambios }) => {
  const frame = useCurrentFrame();
  if (cambios.length === 0) return null;
  let k = 0;
  cambios.forEach((c, i) => {
    if (frame >= c.desde) k = i;
  });
  const actual = cambios[k];
  const cfg = POSES[actual.pose];
  if (!cfg) return null;
  const mismaImagen = k > 0 && cambios[k - 1].pose === actual.pose;
  const esc = CABEZA_ANCHO / cfg.anchoCabeza;
  const w = cfg.ancho * esc;
  const h = cfg.alto * esc;
  const left = CABEZA_X - cfg.cabeza * w;
  const top = PELO_Y - cfg.peloArriba * esc;
  const entrada = spring({ frame: frame - actual.desde, fps: FPS, config: { damping: 20, stiffness: 180, mass: 0.6 } });
  const respira = Math.sin(frame / 22) * 3;
  const escala = (mismaImagen ? 1 : 0.96 + 0.04 * entrada) * (1 + Math.sin(frame / 22) * 0.004);
  const balanceo = Math.sin(frame / 40) * 0.4;
  return (
    <div
      style={{
        position: "absolute",
        left,
        top,
        width: w,
        height: h,
        transform: `translateY(${respira}px) rotate(${balanceo}deg) scale(${escala})`,
        transformOrigin: `${cfg.cabeza * w}px ${1920 - top}px`,
        filter: "drop-shadow(10px 12px 10px rgba(60, 40, 20, 0.28))",
      }}
    >
      <Img src={staticFile(cfg.src)} style={{ width: "100%", height: "100%" }} />
    </div>
  );
};
