// Portada 1080×1920 para Instagram y TikTok. Título y cara dentro del recorte 3:4 de la cuadrícula
// del perfil (y 240–1680). Se configura en plan.json → "portada".
import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import "./motor/fuentes";
import { C, ESTILO, PLAN, POSES, SUAVE } from "./motor/actual";
import { F, alfa } from "./motor/estilos";
import { Fondo } from "./motor/Fondo";
import { Baldosa, Destello } from "./piezas/basicas";

/** true si el color #RRGGBB es oscuro (luminancia baja). */
const esOscuro = (hex: string) => {
  const n = parseInt(hex.replace("#", "").slice(0, 6), 16);
  const [r, g, b] = [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  return 0.2126 * r + 0.7152 * g + 0.0722 * b < 110;
};

const conAcento = (t: string) => t.split(/(\*[^*]+\*)/g).map((s, k) => (s.startsWith("*") ? <span key={k} style={{ color: C.acento }}>{s.slice(1, -1)}</span> : <span key={k}>{s}</span>));

export const Portada: React.FC = () => {
  const p = PLAN.portada ?? { lineas: [PLAN.titulo] };
  const lineas = p.lineas.slice(0, 4);
  const imagenes = (p.imagenes ?? []).slice(0, 4);
  const pose = p.pose && POSES[p.pose] ? POSES[p.pose] : null;
  const largo = Math.max(...lineas.map((l) => l.replace(/\*/g, "").length));
  const tam = Math.min(250, Math.max(84, (940 / (largo * 0.6)) * ESTILO.escalaTitulo));
  // "oscura" solo tiene sentido en estilos claros: en uno oscuro se queda el fondo del estilo
  const oscura = !!p.oscura && !esOscuro(C.fondo);
  const fondo = oscura ? C.oscuro : undefined;
  const fondoOscuro = oscura || esOscuro(C.fondo);
  const colorTexto = oscura ? C.oscuroTexto : C.texto;
  const sombra = SUAVE ? `0 8px 0 ${alfa("#000000", 0.08)}` : `5px 6px 0 ${C.borde}`;
  return (
    <AbsoluteFill style={{ background: fondo }}>
      {!oscura && <Fondo />}
      {p.etiqueta && (
        <div style={{ position: "absolute", left: 0, right: 0, top: 262, display: "flex", justifyContent: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14, background: oscura ? alfa(C.oscuroTexto, 0.12) : C.oscuro, color: C.oscuroTexto, borderRadius: 40, padding: "12px 30px 10px 22px", fontFamily: F.titulo, fontSize: 34, letterSpacing: 3 }}>
            <Destello size={34} />
            {p.etiqueta}
          </div>
        </div>
      )}
      <div style={{ position: "absolute", left: 30, right: 30, top: p.etiqueta ? 360 : 300, textAlign: "center", lineHeight: 1.02, fontFamily: F.titulo, color: colorTexto, textShadow: sombra }}>
        {lineas.map((l, k) => (
          <div key={k} style={{ fontSize: k === 0 ? tam : tam * 0.62, whiteSpace: "nowrap" }}>
            {conAcento(l)}
          </div>
        ))}
      </div>
      {imagenes.map((src, k) => {
        const n = imagenes.length;
        const pos = (k - (n - 1) / 2) / Math.max(1, (n - 1) / 2);
        return (
          <div key={k} style={{ position: "absolute", left: 540 + pos * 300 - 165, top: 900 + Math.abs(pos) * 50, width: 330, height: 220, borderRadius: 24, overflow: "hidden", border: `6px solid ${C.tarjeta}`, transform: `rotate(${pos * 13}deg)`, boxShadow: "0 24px 50px rgba(0,0,0,0.35)", zIndex: Math.round(10 - Math.abs(pos) * 5) }}>
            <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          </div>
        );
      })}
      {imagenes.length === 0 && p.icono && (
        <div style={{ position: "absolute", left: pose ? 600 : 540 - 150, top: 900 }}>
          <Baldosa size={300} icono={p.icono} brillo={0.5} />
        </div>
      )}
      {p.pegatina && (
        <div style={{ position: "absolute", left: 620, top: 1160, transform: "rotate(-7deg)", zIndex: 20 }}>
          <div style={{ background: C.acento, color: C.acentoTexto, fontFamily: F.titulo, fontSize: 42, padding: "14px 26px 12px", borderRadius: 22, boxShadow: "0 16px 30px rgba(0,0,0,0.25)", whiteSpace: "nowrap" }}>{p.pegatina}</div>
        </div>
      )}
      {pose && fondoOscuro && (
        // en fondos oscuros, una luz del color de acento detrás del personaje: lo integra y no parece recortado
        <div style={{ position: "absolute", left: 330 - 440, top: 1150 - 200, width: 880, height: 880, borderRadius: "50%", background: `radial-gradient(circle, ${alfa(C.acento, 0.4)} 0%, ${alfa(C.acento, 0.14)} 45%, ${alfa(C.acento, 0)} 70%)`, zIndex: 14 }} />
      )}
      {pose && (
        <Img
          src={staticFile(pose.src)}
          style={{
            position: "absolute",
            left: 330 - pose.cabeza * pose.ancho * (330 / pose.anchoCabeza),
            top: 1150 - pose.peloArriba * (330 / pose.anchoCabeza),
            width: pose.ancho * (330 / pose.anchoCabeza),
            height: pose.alto * (330 / pose.anchoCabeza),
            filter: fondoOscuro ? `drop-shadow(0 0 1.5px rgba(0,0,0,0.7)) drop-shadow(0 0 50px ${alfa(C.acento, 0.35)})` : "drop-shadow(0 18px 30px rgba(0,0,0,0.35))",
            zIndex: 15,
          }}
        />
      )}
    </AbsoluteFill>
  );
};
