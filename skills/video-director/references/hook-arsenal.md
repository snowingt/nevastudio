# The Hook Arsenal: 12 Battle-Tested Attention Patterns

In short-form video (Reels, TikTok, Shorts), the first 2 seconds determine 80%+ of algorithmic retention. If the viewer's brain registers the content as predictable, generic, or boring within 0–1.5s, they swipe.

This reference details the 12 cognitive hook patterns, their psychological mechanisms, and how to execute them using our native code/video engines.

---

## 1. Pattern Interrupt (Reality Breaking)

### 1.1 Physics Break
- **Mechanism**: The visual breaks expected physical laws (gravity reverses, liquid floats upward, an object freezes mid-shatter). The viewer's visual cortex pauses to resolve the impossibility.
- **Timing**: 0.0s – 0.8s sets normal expectation; 0.8s – 2.0s breaks it abruptly.
- **Engine Execution**:
  - `hand-drawn-canvas-animation`: An object drawn with `wob()` or `blob()` suddenly reverses velocity `vy = -vy * 2`, or particles float upward with negative gravity.
  - `remotion-motion-graphics`: Inverted gravity physics using `@remotion/three` or SVG spring trajectories with negative values.
  - `animate`: Reverse time-lapse curve using custom canvas particle emitters.
- **Audio**: Dead silence or low ambient hum during the normal 0.8s, followed by a resonant whoosh/reverse cymbal right at the break.

### 1.2 Scale Warp
- **Mechanism**: A tiny, everyday object (coin, microchip, valve, key) is rendered massive like a skyscraper, or a city is placed inside a lightbulb. The brain struggles to compute the relative scale.
- **Engine Execution**:
  - `hand-drawn-canvas-animation`: Technical blueprint cross-section where a microscopic pinhole expands to fill the entire 1080×1920 viewport with dimension arrows.
  - `remotion-motion-graphics`: Extreme 3D camera push from micro to macro with depth of field blur (`blur(12px)` $\to$ `blur(0)`).
- **Audio**: Heavy sub-bass drop (40–60 Hz) as the scale reveals itself.

### 1.3 Color Bomb
- **Mechanism**: The frame opens completely desaturated (monochrome, chalkboard, gray ink). At 1.0s – 1.2s, a single focal element ignites with fluorescent neon/amber color, which spreads outward across the canvas.
- **Engine Execution**:
  - `hand-drawn-canvas-animation`: Call `blot()` or `surface()` expanding a saturated colored layer over a grayscale paper texture.
  - `remotion-dev`: CSS `filter: grayscale(1)` transitioning to `grayscale(0)` with an expanding SVG radial clip mask.
- **Audio**: Hard snap or spark SFX + synth hit right on the color burst frame.

---

## 2. Curiosity Gap (Incomplete Information)

### 2.1 Obscured Subject
- **Mechanism**: The camera frames only hands working, concentrated facial expression, or extreme macro detail of a device, deliberately withholding the full picture. The brain demands completion.
- **Timing**: 0.0s – 2.2s tight framing; slight pull-back at 2.3s hints at shape without full reveal.
- **Engine Execution**:
  - `hand-drawn-canvas-animation`: `cam(c, cx, cy, 3.5)` zooming into an internal gear or piston, then easing out to 1.1x at 2.5s.
  - `video-edit`: 4K punch-in crop (300%) on the speaker's eyes or hands before pulling out to standard medium shot.

### 2.2 Reaction Before Action
- **Mechanism**: Show the emotional shock, disbelief, or intense reaction before revealing what caused it. "What are they looking at?" forces the viewer to stay.
- **Engine Execution**:
  - `kinetic`: Pixel avatar eyes widen (`pose: 'shock'`), mouth drops open, sweat droplet pops, before question card slams into frame.
  - `mascota-animada`: Avatar gasps with exclamation marks `(!)` and screen wobble.
- **Audio**: Sharp inhale/gasp SFX followed by a complete 0.3s audio drop.

### 2.3 Countdown Tension
- **Mechanism**: A visual countdown ("3... 2... 1...") creates urgent anticipation. The trick is that the payoff does NOT happen at zero—it transitions into the core thesis.
- **Engine Execution**:
  - `remotion-motion-graphics`: Numbers slam in 3D perspective with spring overshoot (`damping: 12, stiffness: 200`).
  - `kinetic`: Kinetic typography flashing numbers on musical transient beats.
- **Audio**: Ticking clock SFX accelerating into a rising pitch riser.

---

## 3. Dopamine Trigger (Instant Visual Reward)

### 3.1 Satisfying Motion (ASMR-Tier)
- **Mechanism**: Ultra-smooth mechanical movement, liquid pouring, laser cutting, or perfect geometric alignment that triggers soothing ASMR dopamine release.
- **Engine Execution**:
  - `hand-drawn-canvas-animation`: Water droplets condensing on cold metal and trickling down into a clean reservoir with expanding ripple rings.
  - `animate`: Manim-style smooth parametric curve drawing or isometric mechanical gear rotation.
- **Audio**: Crisp high-frequency textures: click, drip, scratch, brush on paper.

### 3.2 Before-After Flash
- **Mechanism**: Split-second comparison between two extreme states (chaos vs order, ugly vs gorgeous, broken vs fixed).
- **Engine Execution**:
  - `remotion-motion-graphics`: Split slider with animated divider bar and spring settle.
  - `hand-drawn-canvas-animation`: Left dirty clogged filter vs right sparkling clean filter with opposing color cards.
- **Audio**: Double impact: low thud on "before", bright shimmer on "after".

### 3.3 Kinetic Typography Slam
- **Mechanism**: Words slam into the screen one by one with heavy physical impact and screen shake, synced to voice rhythm.
- **Engine Execution**:
  - `kinetic`: Automated transient-synced kinetic text pill highlighting each spoken word.
  - `hand-drawn-canvas-animation`: `drawBadge()` with settle bounce (`settle(t, t0, { amp: 0.45, freq: 5 })`).
- **Audio**: Bass-heavy kick drum or sub-thud synced to each word slam.

---

## 4. Primal Attention (Evolutionary Triggers)

### 4.1 Direct Eye Contact
- **Mechanism**: Human/avatar eyes looking dead-straight through the screen. Evolution prioritizes detecting who is watching us.
- **Engine Execution**:
  - `kinetic`: Pixel avatar staring forward, natural blink cycle at 0.5s, head tilt forward on key point.
  - `video-edit`: Direct center-frame gaze alignment with eye-tracking stabilization.

### 4.2 Sudden Peripheral Motion
- **Mechanism**: Frame starts quiet and calm for 0.8s, then an element rapidly enters from outside the screen at high velocity with motion blur.
- **Engine Execution**:
  - `hand-drawn-canvas-animation`: `whip()` camera pan or `smear()` motion blur trails across the viewport.
  - `remotion-dev`: Rapid translation with SVG Gaussian blur filter (`stdDeviation="20 0"`).
- **Audio**: High-speed whoosh / air-displacement sound.

### 4.3 Silence Then Explosion (Audio Contrast)
- **Mechanism**: In a feed full of screaming voices and music, total silence for 1.0s is jarring and causes the thumb to stop. At 1.2s, a crisp acoustic impact fires.
- **Engine Execution**:
  - Mute all audio tracks for frames 0–24 (1.0s).
  - Frame 25: Visual cut + sharp audio transient (snap/kick/clack).
