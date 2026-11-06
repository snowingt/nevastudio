---
name: kinetic
description: "Motor y habilidad de video de tipografía cinética (Kinetic Typography) y motion design sincronizado a la voz, beats y transientes, con avatar pixel art animado y lip-sync, HUD cyberpunk retro y composición determinista sin suscripciones."
license: MIT
---

# Kinetic — Motor de Tipografía Cinética y Motion Design

Reconstrucción e ingeniería inversa independiente de la arquitectura *Scenario Kinetic Music Video / Film Skill* (REA), desacoplada al 100% de APIs propietarias de Scenario y convertida en un motor autónomo local y determinista.

Un audio con voz entra. Un vídeo cinematográfico en vertical 9:16 (1080×1920 a 30/60 fps) o panorámico 16:9 sale:
- **Tipografía Cinética Avanzada:** Palabras que impactan al ritmo exacto de los fonemas y transientes de la voz (*Smear Slam*, *Stagger Rise*, *Scramble Resolve*, *Echo Wall*, *Swiss Grid*, *Karaoke Glow*).
- **HUD & Motion Design:** Retículas, corchetes `[ ]`, barras visualizadoras de espectro de audio reactivas, contadores de tiempo/BPM, líneas de escaneo y destellos en los acentos.
- **Avatar Pixel Art & Lip-Sync:** Integración de la mascota/avatar del creador en pixel art con contorno de pegatina, halo luminoso y sincronización labial palabra por palabra con 7 visemas fonéticos.
- **Rendimiento Puro:** Funciona localmente en Python (Pillow + numpy + faster-whisper + ffmpeg) con renderizado determinista de alta velocidad y cero coste por fotograma.

---

## 📐 Catálogo de Técnicas Cinéticas (Motion Primitives)

1. **Smear Slam:** La palabra impacta en el centro desde una escala 1.6× con 3 ecos semitransparentes que colapsan hacia adentro (`outExpo`) y un destello blanco de 1 fotograma en el acento.
2. **Scramble Resolve:** Glifos de código o ruido binario que se resuelven de izquierda a derecha en la palabra final al hablar.
3. **Echo Wall:** Filas horizontales de texto con contorno que se desplazan en direcciones opuestas alrededor de la palabra central destacada.
4. **Stagger Rise:** Letras que emergen en cascada desde una máscara base en sincronía con cada sílaba.
5. **Swiss Grid:** Cajas y paneles modernistas con rejilla milimétrica donde los titulares encajan limpiamente.
6. **Cyber HUD Layer:** Indicadores técnicos de cabecera, contador de frames, visor de decibelios reactivo y badges de estado.

---

## 🚀 Flujo de Trabajo

### 1. Voz y Alineación con Whisper
El audio se analiza con `faster-whisper` para extraer los timestamps exactos de cada palabra y fonema:
```bash
python3 scripts/alinear.py --guion guion.txt --voz audio.mp3 --salida datos/
```

### 2. Configuración del Vídeo (`kinetic.json`)
Se definen las secciones, titulares cinéticos, técnica por frase, colores y poses del avatar:
```json
{
  "estilo": "cyber",
  "canvas": "portrait",
  "avatar": "personaje",
  "audio": "datos/voz.mp3",
  "palabras": "datos/palabras.json",
  "secciones": [
    {
      "frase": 1,
      "tecnica": "smear_slam",
      "texto": "REVOLUCIÓN",
      "pose": "senala_camara",
      "hud": true
    }
  ]
}
```

### 3. Renderizado Determinista
```bash
python3 scripts/render.py kinetic.json
```
Produce el archivo final `kinetic.mp4` a 1080×1920 a 30 fps listo para Instagram Reels, TikTok y YouTube Shorts.
