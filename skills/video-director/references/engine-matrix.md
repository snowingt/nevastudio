# Engine Routing Matrix: Directing to Native Skills

Unlike external prompt-generation tools that require manual copy-pasting into cloud generators (Seedance/Higgsfield), the **Video Director** routes and compiles each creative vision into our local, autonomous video production skills.

---

## 1. Decision Matrix by Content Type & Goal

| Video Genre / Goal | Target Aesthetic | Recommended Engine (Skill) | Why This Skill |
|---|---|---|---|
| **Science, Physics & Technical Explainers** | Technical sketchbook, ink & chalk blueprint, physical diagrams | `hand-drawn-canvas-animation` | Whole-pose redrawn drawings, `wob`, `hatch`, technical cutaways, offline 24fps render with zero subscription. |
| **Mathematical, Geometric & Procedural Stories** | Manim-style math curves, cut-paper, isometric line art | `animate` | Single-file procedural canvas engine with built-in Web Audio synthesizer and style presets. |
| **Podcast Highlights, Voice Clips & Cyberpunk Shorts** | High-energy HUD, audio-transient kinetic type, pixel avatar | `kinetic` | Audio-reactive transient detection, pixel art character with automated lip-sync, scanlines, and glow. |
| **SaaS Product Launches, App Demos & Web UI** | Keynote-grade floating 3D mockups, perspective zoom, clean UI | `remotion-dev` / `remotion-motion-graphics` | React component-based rendering, SVG animation, spring physics, 4K crisp typography. |
| **Interactive HTML5 Video & Ready-Made Blocks** | 3D models, animated charts, kinetic overlays, transitions | `hyperframes` / `hyperframes-cli` | Web-standards video composition, 450+ installable blocks (glitch, CRT, maps). |
| **Character Brand, Mascot & Step-by-Step Tutorials** | 3D voxel cubes, pixel art, or illustrated cartoon mascot | `mascota-animada` / `becario-reels` / `mascota-cubos` | Autonomous vertical reel pipeline with avatar lip-sync, numbered step cards, and sound effects. |
| **Creator Talking Heads & Real Video Clips** | 4K punch-ins, kinetic words behind head, dead-air removal | `video-edit` | Professional Instagram reel editor with safe-zone checks, automatic take selection, and rotoscoping. |
| **Photorealistic Generative B-Roll & Visual Sequences** | Cinematic photoreal scenes, slow motion, drone camera | `google-flow-automation` (Veo 3.1 / Nano Banana) | Automated batch prompting and browser orchestration on Google Flow. |
| **Automated Stock-Footage Short-Form Reels** | Dynamic captions, pop-spring text, stock/AI montage | `moneyprinterturbo-core` | Batch video assembly with local scene revisioning and voice integration. |

---

## 2. Technical Execution Recipes by Engine

### A. Directing `hand-drawn-canvas-animation`
- **When to Choose**: When the subject benefits from technical breakdown, physical mechanisms, cross-sections, or editorial sketchbook charm (e.g. "How does an engine work?", "Why planes fly", "The history of cryptography").
- **Director Directives**:
  1. Set format: `setFormat({ ar: '9:16', width: 1080 })` for vertical mobile.
  2. Choose palette: `usePalette('paperInk')` or custom technical palette with distinct hot/cold or highlight colors.
  3. Use `camKeys(c, tau, K, { hand: 1.5 })` for organic handheld camera drift.
  4. Build dynamic visual metaphors (cutaways, exploding parts, flowing fluids, thermometers, gauges).
  5. Sincronize live speech caption stickers with word-by-word yellow marker highlights (`drawVoiceCaption`).

### B. Directing `kinetic`
- **When to Choose**: When the driving asset is an audio bite, podcast clip, strong philosophical statement, or fast-paced technical monologue.
- **Director Directives**:
  1. Analyze audio file transients using Web Audio API or ffmpeg silence/beat analysis.
  2. Align kinetic typography slam to audio transients.
  3. Direct the pixel-art avatar's emotions (neutral, talk, shock, question, smirk, confident).
  4. Frame the layout inside 9:16 safe zones (avatar at lower third or upper center, text occupying high-readability center band).

### C. Directing `remotion-motion-graphics`
- **When to Choose**: When launching a tech product, SaaS platform, showcasing a dashboard, or presenting high-polish business metrics.
- **Director Directives**:
  1. Avoid flat screen recordings: direct a floating perspective frame with subtle 3D rotation (`rotateX(10deg) rotateY(-15deg)`).
  2. Implement spring physics on UI elements (`spring({ fps, frame, config: { damping: 15, stiffness: 180 } })`).
  3. Plan the 2-second hook: "The Problem Flash" (chaotic red notifications) $\to$ "One-Click Solution" (clean glowing interface).
  4. Sound sync: Click SFX, subtle whooshes on drawer slides, chime on success state.

### D. Directing `video-edit`
- **When to Choose**: When the user provides raw camera recordings of a person talking.
- **Director Directives**:
  1. Cut dead air aggressively (tight cadence without breathing gaps).
  2. Direct 4K punch-ins (zoom 1.15x – 1.3x on punchy punchlines).
  3. Place bold kinetic text behind the speaker's head using automatic mask separation.
  4. Ensure all subtitles and graphics remain within the Instagram Reels / TikTok safe zone (padding 180px top, 240px bottom).

---

## 3. The Sound Stack Directives

Every directed video must specify 4 audio layers:
1. **Voice / Narration**: Clean, centered, compressed, sidechain ducking the score by -10dB.
2. **Impacts & Accents**: Low-frequency kicks (50Hz) or sharp clacks on visual cuts, stamps, and hook reveals.
3. **Risers & Tension**: Subtle rising synth or ticking acceleration before key reveals.
4. **Foley & ASMR Textures**: Contextual acoustic details (chalk on board, fluid bubbling, keyboard keystrokes, metallic clicks) placed at 20-30% volume.
