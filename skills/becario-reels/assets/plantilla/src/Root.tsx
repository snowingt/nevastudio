import React from "react";
import { AbsoluteFill, Composition, Img, Still } from "remotion";
import { FPS } from "./motor/constantes";
import { TOTAL, resumen } from "./motor/linea";
import { Portada } from "./Portada";
import { Reel } from "./Reel";

// Hoja de contacto: los fotogramas ya renderizados (en JPEG pequeño, como data URL) en una cuadrícula.
const COLS = 6,
  MW = 300,
  MH = 533,
  ETQ = 34;
type Tesela = { src: string; etiqueta: string };
const Mosaico: React.FC<{ teselas: Tesela[] }> = ({ teselas }) => (
  <AbsoluteFill style={{ background: "#161616" }}>
    {teselas.map((t, k) => (
      <div key={k} style={{ position: "absolute", left: (k % COLS) * MW, top: Math.floor(k / COLS) * (MH + ETQ), width: MW, height: MH + ETQ }}>
        <div style={{ height: ETQ, color: "#FFD400", font: "bold 22px sans-serif", padding: "5px 8px", whiteSpace: "nowrap", overflow: "hidden" }}>{t.etiqueta}</div>
        <Img src={t.src} style={{ width: MW, height: MH, display: "block" }} />
      </div>
    ))}
  </AbsoluteFill>
);

// Comprobación de la portada: entera, recortada a 3:4 (cuadrícula del perfil) y en miniatura.
const PortadaCheck: React.FC = () => (
  <AbsoluteFill style={{ background: "#161616", color: "#FFD400", font: "bold 26px sans-serif" }}>
    <div style={{ position: "absolute", left: 10, top: 8 }}>9:16 completa</div>
    <div style={{ position: "absolute", left: 0, top: 44, width: 540, height: 960, overflow: "hidden" }}>
      <div style={{ width: 1080, height: 1920, transform: "scale(0.5)", transformOrigin: "0 0" }}>
        <Portada />
      </div>
    </div>
    <div style={{ position: "absolute", left: 580, top: 8 }}>recorte 3:4 del perfil</div>
    <div style={{ position: "absolute", left: 570, top: 44, width: 540, height: 720, overflow: "hidden" }}>
      <div style={{ width: 1080, height: 1920, transform: "scale(0.5) translateY(-240px)", transformOrigin: "0 0" }}>
        <Portada />
      </div>
    </div>
    <div style={{ position: "absolute", left: 1140, top: 8 }}>cuadrícula</div>
    <div style={{ position: "absolute", left: 1140, top: 44, width: 150, height: 200, overflow: "hidden" }}>
      <div style={{ width: 1080, height: 1920, transform: `scale(${150 / 1080}) translateY(-240px)`, transformOrigin: "0 0" }}>
        <Portada />
      </div>
    </div>
  </AbsoluteFill>
);

export const RemotionRoot: React.FC = () => (
  <>
    {/* calculateMetadata devuelve el resumen (escenas, momentos, problemas) para `node render.mjs resumen` */}
    <Composition id="Reel" component={Reel} durationInFrames={TOTAL} fps={FPS} width={1080} height={1920} calculateMetadata={async () => ({ props: { resumen: resumen() } })} />
    <Still id="Portada" component={Portada} width={1080} height={1920} />
    <Still id="PortadaCheck" component={PortadaCheck} width={1310} height={1010} />
    <Still
      id="Mosaico"
      component={Mosaico}
      width={COLS * MW}
      height={MH + ETQ}
      defaultProps={{ teselas: [] as Tesela[] }}
      calculateMetadata={async ({ props }) => ({ height: Math.max(1, Math.ceil(props.teselas.length / COLS)) * (MH + ETQ) })}
    />
  </>
);
