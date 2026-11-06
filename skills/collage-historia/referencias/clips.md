# Clips, imágenes y derechos

## De dónde salen
- **Solo el material que aporte el usuario.** No descargues películas, series ni vídeos de internet.
- Si la historia es una fábula, un mito o un hecho histórico, puede usar imágenes propias, dibujos hechos con IA o material de dominio público, o solo los iconos y recortes de la skill.

## Cómo usarlos
- **Trozos cortos** (1,5–4 s) y **sin su audio** (`trozos.py cortar`, que por defecto lo quita). Las citas con su audio, solo en la versión B y en tramos cortos.
- Siempre **comentados**: el vídeo cuenta algo propio y el clip lo ilustra. Nunca escenas seguidas que cuenten la película.
- **Con la fuente**: en el pie de foto (`fuente_clips`) y en la descripción del vídeo.
- No redibujes personajes de otros ni copies o traduzcas su guion. Las citas, cortas y entre comillas.
- Avisa al usuario: aunque los trozos sean cortos y comentados, **las plataformas pueden silenciar, limitar o bloquear el vídeo** si detectan material con derechos. Es decisión suya usarlo.

## Elegir momentos sin gastar
1. `trozos.py hoja CLIP.mp4`: una sola imagen con una miniatura cada 2 s (o `--cada 1`). Mírala con la herramienta de leer imágenes.
2. `trozos.py transcribir CLIP.mp4`: lo que se dice, con su segundo. Para las citas, escucha el tramo: la transcripción automática se equivoca.
3. `trozos.py cortar CLIP.mp4 DESDE HASTA nombre --carpeta P/clips`. Apunta en `P/clips/lista.txt` de dónde sale cada trozo (lo hace solo).

## Imágenes y personaje
- Imágenes en `P/imagenes/`: PNG con fondo transparente quedan mejor (salen como pegatina). Si el fondo es liso, se quita solo; si no, sale como foto con borde blanco.
- Personaje en `P/personaje/`: una PNG por pose (`saluda.png`, `sorpresa.png`…), todas con la cabeza más o menos del mismo tamaño. Se escalan a la misma altura (`"alto"` en `personaje`).
