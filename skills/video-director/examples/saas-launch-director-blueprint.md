# Example: Directing a SaaS Product Launch (Engine: Remotion Motion Graphics)

### Brief
"A 12-second vertical product launch for an AI task manager called 'Pulse'. Dark mode UI, minimal aesthetic, high energy."

---

### Director's Blueprint

- **Archetype**: 02. SaaS & Tech Product Launch
- **Selected Engine**: `remotion-motion-graphics`
- **Format**: 9:16 Vertical (1080×1920), 30 FPS, 12.0s (360 frames)
- **Primary Hook (0.0s – 2.0s)**: *The Problem Flash + The One-Click Magic*

#### Beat-by-Beat Timeline

| Time | Frame | Visual Action | Camera Move | Sound Stack (4 Layers) | Kinetic Typography |
|---|---|---|---|---|---|
| 0.0s – 1.0s | 0–30 | 5 chaotic red notification cards flash violently across the screen at different depths (0.2s each). | High-frequency camera jitter (`amp: 4px`). | **Voice**: "Tired of software chaos?"<br>**Impact**: Rapid error buzzes.<br>**Ambient**: None. | *"CHAOS"* in bold red slab serif, vibrating. |
| 1.0s – 2.2s | 30–66 | Sudden snap cut to black. Sleek obsidian smartphone floats in center void at 15° 3D tilt. Glowing cyan cursor approaches a single button. | Smooth slow push-in (`scale: 1.0 -> 1.08`). | **Voice**: "Meet Pulse."<br>**Impact**: Sub-bass drop (50 Hz).<br>**Foley**: Glass chime + laser hum. | *"PULSE"* appears in clean letter-spaced grotesque. |
| 2.2s – 6.5s | 66–195 | Cursor clicks button. A vibrant cyan shockwave expands across the interface. 40 chaotic tasks automatically collapse and sort into 3 elegant priority cards with smooth spring physics (`damping: 14`). | Camera glides 20° orbit around device showing 3D depth and subtle glass reflection. | **Voice**: "One click. All your tasks organized instantly."<br>**Impact**: Satisfying deep mechanical switch click.<br>**Riser**: Uplifting synth progression. | Floating badge: `[ AUTO-ORGANIZED IN 0.2s ]`. |
| 6.5s – 9.5s | 195–285 | Camera pushes straight through the device glass into full-screen UI. Interactive analytics chart draws itself with glowing particle trail. | Fast perspective zoom into screen with soft blur transition. | **Voice**: "Save 12 hours every week."<br>**Foley**: Data counter tick (fast accelerating). | Large numbers tick rapidly: `0h -> 12h / week`. |
| 9.5s – 12.0s | 285–360 | UI pulls back into centered hero badge. Elegant glowing CTA button pulses. Particle embers float gently in the dark void. | Settle zoom holding at 1.0x with gentle breathing drift. | **Voice**: "Try Pulse free today. Link in bio."<br>**Impact**: Crisp final kick + soft tail echo. | *"START FREE TODAY"* with glowing border. |

---

### Implementation Instructions for `remotion-motion-graphics`
1. Use `@remotion/three` or 3D CSS transforms `perspective(1200px) rotateX(12deg) rotateY(-8deg)`.
2. Cards animate using `spring({ frame, fps, config: { damping: 14, stiffness: 160 } })`.
3. Background uses radial gradient: `radial-gradient(circle at 50% 40%, #1e1b4b 0%, #030712 70%)`.
4. Render with: `npx remotion render src/index.ts PulseLaunch out/pulse_launch.mp4`.
