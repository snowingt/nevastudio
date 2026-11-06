// Plantilla de escena propia. Cópiala, cambia el nombre y regístrala en propias/index.ts.
//
// Reglas para que encaje con el resto del vídeo:
// - Dibuja dentro del lienzo: x 60–1020, y 210–1070 (centro 540, 640). El motor lo escala si hace falta.
// - Usa los colores con nombre de uso (C.acento, C.tarjeta, C.texto…) y las fuentes F.titulo, F.texto, F.mano, F.mono.
// - Cada elemento entra en un momento de `b` (fotogramas desde el inicio de la escena), que viene de "en" en el plan.
// - Que siempre se mueva algo: un elemento nuevo como mucho cada 0,6 s (18 fotogramas).
import React from "react";
import { AbsoluteFill, spring, useCurrentFrame } from "remotion";
import { C } from "../motor/actual";
import { FPS } from "../motor/constantes";
import { F } from "../motor/estilos";
import { useFlota } from "../motor/anim";
import { Icono, Pildora, Tarjeta } from "../piezas/basicas";
import type { DefEscena, PropsEscena } from "../tipos";
import { txt } from "../escenas/util";

const Ejemplo: React.FC<PropsEscena> = ({ p, b }) => {
  const f = useCurrentFrame();
  const [b0, b1] = b;
  const entra = spring({ frame: f - b0, fps: FPS, config: { damping: 14, stiffness: 150, mass: 0.7 } });
  const fl = useFlota(0.5, 6, 15);
  return (
    <AbsoluteFill>
      <Tarjeta x={190} y={330 + fl} w={700} h={460} transform={`scale(${entra})`}>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", gap: 30 }}>
          <Icono nombre={txt(p, "icono", "sparkles")} tam={150} />
          <div style={{ fontFamily: F.titulo, fontSize: 64, color: C.tarjetaTexto }}>{txt(p, "titulo", "Mi escena")}</div>
        </div>
      </Tarjeta>
      {f >= b1 && (
        <div style={{ position: "absolute", left: 0, right: 0, top: 860, display: "flex", justifyContent: "center" }}>
          <Pildora fondo={C.acento} color={C.acentoTexto}>
            {txt(p, "etiqueta", "¡listo!")}
          </Pildora>
        </div>
      )}
    </AbsoluteFill>
  );
};

export const ejemplo: DefEscena = {
  C: Ejemplo,
  momentos: 2,
  sonidos: () => [
    [0, "pop", 0.3],
    [1, "ding", 0.25],
  ],
};
