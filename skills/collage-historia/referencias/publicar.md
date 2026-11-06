# Publicar

## Archivos
- `salida/<nombre>_instagram.mp4` y, si hay segundo final, `salida/<nombre>_tiktok.mp4` (1080×1920, 30 fps, H.264, voz a −14 LUFS).
- `salida/portada.png`: la misma para las dos redes. Mira `portada_comprobar.png`: el título y el número tienen que leerse en el recorte 3:4 y a 120 px.
- Si un vídeo pesa más de lo que admite donde lo subes, recomprímelo: `ffmpeg -i entrada.mp4 -c:v libx264 -crf 21 -preset veryfast -c:a copy salida.mp4`.

## Textos
- **Instagram:** la primera línea es el gancho (no hay título); luego qué cuenta el vídeo en 2–3 líneas, la llamada a la acción y 3–5 hashtags. La fuente de los clips al final («Clips: Título (Estudio, año)»).
- **TikTok:** se ven unos 100 caracteres antes de «más»: la primera línea, con lo que la gente buscaría. Misma estructura y 3–5 hashtags.
- Solo lo que se puede comprobar. Nada de «esto lo cambia todo».

## Antes de publicar
- Marca el vídeo como **contenido hecho con IA** si la voz es sintética o hay imágenes generadas (TikTok: «Más opciones» → «Contenido generado por IA»; Instagram: «Añadir etiqueta de IA»). Los nombres del menú pueden cambiar.
- Si el final dice «comenta PALABRA», que el usuario tenga preparado lo que va a mandar **antes** de publicar.
- En TikTok, sube la portada desde la galería antes de publicar (después no se puede cambiar).
