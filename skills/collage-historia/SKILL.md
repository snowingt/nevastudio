---
name: collage-historia
description: Vídeos verticales en collage de revista que cuentan una historia (película, serie, fábula o hecho real) aplicada a tu tema, con tus clips. Elige la historia, escribe el guion y monta el vídeo.
---

# collage-historia

Hace vídeos verticales (1080×1920, 30 fps) para Reels, TikTok o Shorts con este formato:
- **Una historia conocida como metáfora de tu tema**: una película, una serie, una fábula, un mito o un hecho real («un villano predijo hace 20 años lo que pasa hoy con…»).
- **Estilo collage de papel dinámico**: titulares recortados como de revista, pegatinas, sellos, etiquetas, notas e iconos.
- **5 Reglas de Fluidez Cinética (Anti-PowerPoint)**:
  1. *Máscaras de texto*: Titulares y palabras clave reveladas mediante máscaras deslizantes (`clip-path`).
  2. *Empuje encadenado*: Sellos y pegatinas impactan con retroceso elástico y desplazan los elementos contiguos.
  3. *Cámara guiada*: Encuadre dinámico que hace zoom al detalle activo y panea con la acción.
  4. *Expansión morfométrica*: Papeles o tarjetas que se desgarran o expanden para llenar la pantalla y dar paso a la siguiente escena.
  5. *Sincronización sonora*: Sonidos de papel, sellos y clics mecánicos fijados a cada palabra y número.
- **Subtítulos palabra a palabra** con las palabras clave en una caja de color, y, si el usuario lo quiere, **su personaje** abajo a la izquierda cambiando de pose.
- **Dos finales** (por ejemplo, uno para Instagram y otro para TikTok) sin montar dos veces, y una versión opcional en la que **las citas suenan con el audio original** del clip.

Todo se hace con Python (Pillow y numpy) y ffmpeg. No hace falta navegador ni programas de vídeo de pago.

## Antes de empezar
1. Copia la skill a una carpeta de trabajo (la carpeta de la skill es de solo lectura) y comprueba el entorno:
   ```bash
   mkdir -p ~/collage-historia && cp -r <carpeta de esta skill>/. ~/collage-historia/ && chmod -R u+w ~/collage-historia && cd ~/collage-historia && python3 scripts/comprobar.py
   ```
   El `chmod` hace falta porque `cp -r` conserva el «solo lectura». Si algo sale con ✗, arréglalo antes de seguir: la comprobación instala lo que puede.
2. Un proyecto por vídeo, por ejemplo `~/collage-historia/proyectos/mi-video/`. Todos los comandos se lanzan desde `~/collage-historia`; abajo, `P` es la carpeta del proyecto.
3. **¿Primera vez, o el usuario aún no tiene clips?** Monta el ejemplo (una fábula, con clips dibujados por código; unos 2 minutos):
   ```bash
   mkdir -p proyectos && cp -r ejemplo proyectos/prueba
   python3 ejemplo/crear_ejemplo.py proyectos/prueba
   python3 scripts/alinear.py --guion proyectos/prueba/guion.txt --sin-voz --salida proyectos/prueba/voz
   python3 scripts/render.py proyectos/prueba/video.json
   ```
   El vídeo sale en `proyectos/prueba/salida/`, sin voz. Sirve para ver el estilo y comprobar que todo funciona.

## El trabajo, paso a paso

### 1. La historia → `referencias/historia.md`
Pregunta en **un solo mensaje**, con opciones cerradas si puedes:
- **Tema** del vídeo y **qué quiere que se lleve** quien lo vea (una frase).
- **¿Tiene ya una historia?** Si no, propón **tres** que encajen (una de cine o serie, una fábula o mito y un hecho real), con el paralelismo en una línea cada una, y que elija.
- **Clips:** qué clips tiene de esa historia. Solo se usan **los que aporte el usuario**: no descargues películas ni series.
- **Voz:** si grabará su voz o la generará (por ejemplo, con ElevenLabs), o si de momento lo quiere sin voz.
- **Palabra para comentar** y si quiere dos finales.

Si no contesta, sigue con lo razonable (la primera historia propuesta, sin voz, un solo final) y dilo.

### 2. Guion → `referencias/historia.md`
- `P/guion.txt`, con **una frase por línea**: 12–18 frases (55–75 s) o, si lo quiere corto, 8–11 (30–45 s), a unas 195 palabras por minuto.
- **La última línea es el final** («Comenta PALABRA…» o «Sígueme…»): `plan.py` y `finales.py` la tratan como tal.
- Estructura: gancho con un dato concreto → la historia en 6–8 frases (quién, qué quería, qué pasó, la frase clave) → «¿Te suena?» y el paralelismo con el tema → el matiz o la objeción → la idea que se lleva → llamada a la acción.
- Marca entre `**dos asteriscos**` las palabras clave: salen en la caja de color de los subtítulos.
- **Comprueba los datos** (años, nombres, cifras) en una fuente fiable y **las citas** escuchando el clip (`trozos.py transcribir`). No inventes frases de personajes.
- Si la voz será de ElevenLabs, dale además el texto con etiquetas de emoción y las palabras extranjeras escritas como suenan (`referencias/historia.md`).

### 3. Clips → `referencias/clips.md`
```bash
python3 scripts/trozos.py hoja CLIP.mp4                      # hoja de miniaturas con el segundo de cada una (CLIP_hoja.png, junto al clip)
python3 scripts/trozos.py transcribir CLIP.mp4               # qué se dice y cuándo (CLIP_transcripcion.txt, junto al clip)
python3 scripts/trozos.py cortar CLIP.mp4 12.0 14.5 escena_clave --carpeta P/clips   # trozo corto, sin audio
```
- Mira la hoja (es una sola imagen) en lugar de fotogramas sueltos. Trozos de **1,5–4 s**, sin el audio del clip.
- Imágenes sueltas (PNG, mejor con fondo transparente) en `P/imagenes/`. Poses del personaje (PNG) en `P/personaje/`, una por archivo, con el nombre de la pose (`saluda.png`).

### 4. Voz y tiempos
```bash
python3 scripts/alinear.py --guion P/guion.txt --voz audio.mp3 --salida P/voz [--velocidad 1.05]   # con voz
python3 scripts/alinear.py --guion P/guion.txt --sin-voz --salida P/voz                            # sin voz
```
- Recorta las pausas largas, deja la voz a −14 LUFS y saca el momento de cada palabra con Whisper. La primera vez descarga el modelo (unos 240 MB, en `~/.cache/collage-historia/`; funciona sin permisos de administrador).
- Si salen menos del 80 % de palabras reconocidas, `guion.txt` no coincide con lo que dice la voz: corrígelo y repite.
- Si dice que la voz va lenta (menos de 185 por minuto), repite con `--velocidad 1.05` (acelera sin cambiar el tono).

### 5. Plan → `referencias/plan.md`
```bash
python3 scripts/plan.py P --fuente "Título (Estudio, año)" [--palabra PALABRA] [--dos-finales]   # borrador de P/video.json
```
El borrador funciona, pero es solo un punto de partida (un clip por frase y titulares sacados de las negritas): **revísalo frase a frase** y elige para cada una el clip o el elemento que muestre lo que se dice. Lo esencial:
- Un objeto en `"frases"` por cada línea del guion, en el mismo orden.
- **Titular** de 2–4 palabras por línea; la segunda línea entra con una palabra: `"LO PREDIJO@predijo"`.
- **2–3 elementos por frase** en la zona central (y = 450–1280), cada uno entrando con la palabra que lo nombra (`"en": "botas"`): clip, imagen, sello, etiqueta, precio, nota, icono, pasos, cuadrícula, tachado, rasgado o frase en grande.
- **El primer elemento entra en el primer segundo** (gancho) y algo cambia en cada zona al menos cada 0,6 s.
- Copia la estructura de `ejemplo/video.json`.

### 6. Revisar y montar
```bash
python3 scripts/render.py P/video.json --muestras    # una miniatura por frase → P/salida/muestras_N.png, y avisos
python3 scripts/render.py P/video.json --en 12.5     # un fotograma a tamaño real
python3 scripts/render.py P/video.json               # vídeo → P/salida/<nombre>_instagram.mp4
python3 scripts/ritmo.py P/salida/<nombre>_instagram.mp4 --por-zona
python3 scripts/portada.py P/video.json              # portada.png + portada_comprobar.png
```
- **Mira las muestras antes del vídeo** y arregla los avisos: cosas que se pisan, que invaden el titular o los subtítulos, titulares largos y **zonas vacías** («Ritmo: zona centro vacía…»). Al acabar el vídeo, `render.py` pasa también el control de ritmo y avisa si algo se queda quieto.
- Enseña al usuario 3 o 4 fotogramas a tamaño real (`--en`) antes del vídeo completo.
- El render va más o menos a tiempo real y se hace por tandas: si el proceso se corta, repite el mismo comando y sigue donde iba.
- Si `ritmo.py` avisa, añade en ese segundo un elemento con `"en"`, una línea de titular con `@` o un cambio de pose (`"poses"`), y vuelve a montar.

### 7. Dos finales y citas originales → `referencias/plan.md`
- **Segundo final** (por ejemplo, TikTok): el usuario graba solo la última frase. Luego:
  ```bash
  python3 scripts/finales.py --voz P/voz --final final_tiktok.mp3 --texto "Sígueme y escríbeme PALABRA por privado." --salida P/voz_tiktok
  python3 scripts/render.py P/video.json --final tiktok      # reutiliza el cuerpo: solo monta el final
  ```
  En `video.json`, `"final_tiktok"` es la última frase de ese final.
- **Versión con las citas originales** (opcional): describe cada cita en `P/citas.json` y:
  ```bash
  python3 scripts/citas.py --voz P/voz --citas P/citas.json --salida P/voz_b
  python3 scripts/render.py P/video.json --voz voz_b --sufijo b
  ```
  En la versión con citas, los subtítulos dicen lo que dice el audio del clip (de `texto`: `citas.py` avisa si no coincide), y un clip con `"con_cita": true` arranca justo cuando suena. Si en la B un sello o un titular ya no encaja, usa `titular_b` y `"versiones"` (`referencias/plan.md`).

### 8. Entrega → `referencias/publicar.md`
- Manda al usuario los vídeos y la portada, y escríbele los textos para cada red (con la fuente de los clips).
- Recuérdale marcarlo como contenido hecho con IA si la voz es sintética.
- Si el final dice «comenta PALABRA», pregúntale qué mandará a quien comente.

## Reglas
- **Clips de otros:** solo los que aporte el usuario, en trozos cortos, comentados y con la fuente. No redibujes personajes de otros ni copies su guion. Avísale de que las plataformas pueden silenciar o bloquear un vídeo por derechos aunque los trozos sean cortos (`referencias/clips.md`).
- **Datos y citas comprobados:** fechas, cifras y frases, de una fuente fiable o del propio clip. Si algo no se ha comprobado, dilo.
- Sin logos de empresas dibujados: las marcas, solo como texto.
- Si algo falla, mira `referencias/problemas.md` antes de improvisar.

## Archivos
- `scripts/`: `comprobar.py`, `trozos.py`, `alinear.py`, `plan.py`, `render.py` (motor), `collage.py` (piezas de papel e iconos), `finales.py`, `citas.py`, `ritmo.py`, `portada.py`, `sonidos.py` (efectos sintetizados) y `comun.py`.
- `referencias/`: `historia.md`, `clips.md`, `plan.md`, `publicar.md` y `problemas.md`.
- `ejemplo/`: guion, plan y `crear_ejemplo.py` (fábula de la liebre y la tortuga, con material dibujado por código).
- `fuentes/`: Poppins y Lora, con licencia OFL.
