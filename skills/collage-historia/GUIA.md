# collage-historia · guía rápida

## Qué es
Una skill para Claude que hace vídeos verticales (Reels, TikTok, Shorts) en **estilo collage de revista** a partir de **una historia conocida** (una película, una serie, una fábula o un hecho real) que se aplica a tu tema. Te ayuda a **elegir la historia**, te **escribe el guion** y **monta el vídeo** con tus clips: titulares recortados, clips enmarcados como fotos, pegatinas, sellos, subtítulos palabra a palabra, tu personaje si lo tienes, dos finales (por ejemplo, uno para Instagram y otro para TikTok) y la portada.

## Qué necesitas
- Un plan de pago de Claude (**Pro, Max, Team o Enterprise**): las skills no están en el plan gratuito (según la ayuda oficial de Claude, consultada el 31-10-2026). Y la **ejecución de código activada** (Ajustes → Capacidades).
- Tus clips de la historia (trozos cortos), tu voz o una voz generada (por ejemplo, con ElevenLabs) y, si quieres, las poses de tu personaje en PNG.

## Cómo se instala
1. En Claude, activa la ejecución de código (Ajustes → Capacidades → Ejecución de código).
2. Personalizar → Skills → + → **Subir una skill**, y sube el ZIP tal cual (sin descomprimir).
3. Abre un chat nuevo y escribe lo de abajo.

## Un ejemplo para probarla
> Usa la skill collage-historia y monta el vídeo de ejemplo de la liebre y la tortuga.

Tarda unos minutos y te da un vídeo de unos 35 s, sin voz, con clips dibujados por código. Después, para el tuyo:
> Usa la skill collage-historia. Quiero un vídeo sobre [tu tema]. Propónme tres historias que encajen.

Te preguntará lo que falte, te dará el guion (y el texto para grabar la voz), y cuando le pases la voz y los clips, montará el vídeo.

## Si algo falla
- **«Read-only file system» o «Permission denied»:** dile «copia la skill a una carpeta de trabajo como dice SKILL.md» (hay que copiarla con `chmod -R u+w`).
- **No reconoce bien la voz:** el texto del guion tiene que ser lo mismo que dice el audio. Pásale el texto exacto.
- **El vídeo se corta a medias:** pídele que repita el mismo comando; sigue donde iba.
- **Tu clip no sale:** comprueba que lo has subido al chat y que es un vídeo normal (MP4 o MOV).
- Más casos en `referencias/problemas.md`.

## Ojo con los derechos
Usa solo clips que tengas, en trozos cortos, comentados y con la fuente. Aun así, Instagram, TikTok o YouTube pueden silenciar o limitar un vídeo que lleve material de otros: la decisión es tuya.

## Licencias
- Código de la skill: puedes usarlo y modificarlo libremente para tus vídeos.
- Fuentes: Poppins y Lora, con licencia SIL Open Font License (en `fuentes/`).
- Reconocimiento de voz: faster-whisper (MIT) con el modelo Whisper small (MIT). Se descarga la primera vez (unos 240 MB) desde Hugging Face o, si no se puede, desde los paquetes de npm @skillninja/shortmovie-telop-model-p0 a p3, y se comprueba con su sha256.
- Efectos de sonido: sintetizados por código. Iconos, papeles y el material del ejemplo: dibujados por código para esta skill.

---
Hecha por **@elbecariodemurphy.ia** · versión 1.0
