# Local Audio Library & Sound Design Stack

Esta guía documenta la librería de audio local disponible en la máquina y cómo integrarla en las producciones audiovisuales dirigidas con `video-director`, `hand-drawn-canvas-animation`, `kinetic`, `remotion-motion-graphics`, y demás motores.

---

## 1. Ubicaciones Principales

| Categoría | Ruta en el Sistema | Contenido |
|---|---|---|
| **Efectos de Sonido (SFX)** | `/home/snow/Music/sound effect/6 - Sound Effects-20260531T191224Z-3-001/6 - Sound Effects/` | 462 efectos profesionales (Hits, Whooshes, W2H, Risers, Foleys, Anime, Electricidad, Fuego, Vidrio) |
| **Música de Fondo (BGM)** | `/home/snow/Music/playlist/` | Más de 5,000 pistas clasificadas en playlists (Chill House, Deep House, Melodic Techno, Tech House, Afro House, etc.) |
| **Micro-SFX & UI** | `/home/snow/reel_clima/public/sonidos/` & `/home/snow/cubos_studio/motor/sfx/` | Clicks, dings, pops, burbujas, sonidos de proyector y UI suave |

---

## 2. Catálogo de Efectos de Sonido (462 SFX)

### A. W2H (Whoosh-to-Hit) - Transiciones de Alto Impacto (23 archivos)
El estándar de oro en edición moderna (Reels / TikTok / YouTube Shorts) para pasar de una escena a otra:
- `W2H 01.wav` hasta `W2H 05.wav`
- `W2H Airy 01.wav`
- `W2H Complex Heavy Reverse Suction 01-04.wav`
- `W2H Heavy Slam 01.wav`
- `W2H Metal Reverb Suction 01-02.wav`
- `W2H Reverse Suction Impact 01.wav`

### B. Impactos y Golpes (Hits & Slams - 81 archivos)
Ideales para aparición de sellos (*¡FALSO!*, *ERROR*, datos clave, ganchos):
- `Hit Slam Metal 01-04.wav`
- `Hit Impact Slam 01.wav`
- `Hit Complex Eerie 01.wav`
- `Hit Blast Digital Reverb 01.wav`
- `Hit Burst Bass Explosion 01.wav`
- `Explosion Hit Blast 10.wav`
- `sword impact.mp3`, `Kick impact.mp3`

### C. Whooshes y Movimiento Dinámico (176 archivos)
Para paneos rápidos, zooms agresivos, barridos de cámara y objetos que cruzan:
- `fast woosh.mp3`, `bass woosh #1 & #2.mp3`
- `glitchy woosh.mp3`, `slow woosh.mp3`
- `SFX Whoosh Feedback Swell 01.wav`
- `Whoosh Airy Rumble Movement Passby 01.wav`
- Carpeta `Wooshes/`: `14th Woosh.mp3`, `9th Woosh.wav`, `22nd Woosh.mp3`...

### D. Risers y Buildups (Tensión / Revelaciones - 9 archivos)
Para crear anticipación antes del giro o respuesta en la narrativa:
- `Heavy Buildup Sound Effect By Techno.mp3`
- `build up #1.mp3`, `build up #2.mp3`, `build up #3.mp3`
- `H2W Ramp 01.wav`
- `beat slowing.mp3`

### E. Elementos y Foley Orgánico
- **Electricidad** (`Electric/`, 16 archivos): `Electricity 1` al `16.mp3`, chispazos, arcos voltaicos.
- **Fuego** (`Fire/`, 15 archivos): `Fire 1` al `8.wav`, llamaradas, fuego sfx.
- **Vidrio / Rupturas** (`Others/`): `Breaking glass sound effect.m4a`, `SFX Whoosh Shatter Debris Swirl 01.wav`.
- **Atmósfera / Clima**: `Wind - Sound Effect.mp3`, `Weather Snow Moving 06.wav`, `Thunder_Sound_effect.mp3`.
- **Anime SFX**: `Anime woosh.wav`, `DB Dash.wav`, `Bone Crack 1-2.mp3`, `Rock break.wav`, `Tension.wav`.

---

## 3. Integración en el Stack de 4 Capas de Video Director

```
┌─────────────────────────────────────────────────────────────┐
│ Capa 1: Voz Narración (Master TTS / 0 dB)                   │
├─────────────────────────────────────────────────────────────┤
│ Capa 2: Música Fondo (Chill/Deep House / -18 dB a -22 dB)   │
├─────────────────────────────────────────────────────────────┤
│ Capa 3: SFX Estructurales (W2H en cortes, Hit en stamps)    │
├─────────────────────────────────────────────────────────────┤
│ Capa 4: Micro-Foley (Vidrio roto en gancho, chispas, viento)│
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Herramienta Helper para Búsqueda y Uso Rápido

Ejecuta el script utilitario para encontrar audios al instante:

```bash
# Buscar sonidos por palabra clave
python3 /home/snow/.gemini/config/skills/video-director/scripts/sfx_helper.py search "impact"
python3 /home/snow/.gemini/config/skills/video-director/scripts/sfx_helper.py search "whoosh"
python3 /home/snow/.gemini/config/skills/video-director/scripts/sfx_helper.py search "glass"

# Ver preset de sonidos recomendados para el gancho de 2 segundos
python3 /home/snow/.gemini/config/skills/video-director/scripts/sfx_helper.py hook-preset

# Ver géneros musicales disponibles
python3 /home/snow/.gemini/config/skills/video-director/scripts/sfx_helper.py music
```

---

## 5. Mezcla Automática con FFmpeg (Ejemplo)

Para combinar voz, fondo musical y un impacto SFX en el segundo 1.2:

```bash
ffmpeg -y \
  -i voz.wav \
  -i /home/snow/Music/playlist/"Chill House"/track1.mp3 \
  -i "/home/snow/Music/sound effect/6 - Sound Effects-20260531T191224Z-3-001/6 - Sound Effects/Hit Slam Metal 01.wav" \
  -filter_complex "\
    [0:a]volume=1.0[v]; \
    [1:a]volume=0.12[m]; \
    [2:a]adelay=1200|1200,volume=0.85[sfx1]; \
    [v][m][sfx1]amix=inputs=3:duration=first:dropout_transition=2[aout]" \
  -map "[aout]" master_audio.wav
```
