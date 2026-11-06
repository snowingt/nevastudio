# video.json: el plan del vídeo

Rutas relativas a la carpeta de `video.json`. Mira `ejemplo/video.json` para un plan completo.

## Campos generales
| Campo | Qué es |
| --- | --- |
| `nombre` | Nombre de los vídeos de salida (`<nombre>_instagram.mp4`). Si no está, el de la carpeta. |
| `estilo` | `arena` (fondo crema, por defecto), `noche` (fondo azul oscuro) o `rosa`. |
| `colores` | Para cambiar colores sueltos: `{"acento": "#2E86DE", "fondo": "#F2E8D5"}` (también `texto`, `papel`, `rojo`, `periodico`, `sombra`). |
| `voz` | Carpeta de la voz alineada (por defecto `voz`). `voz_tiktok`, la del segundo final. |
| `clips` | `{"clave": "clips/archivo.mp4"}`. Los elementos se refieren a la clave. |
| `imagenes` | `{"clave": "imagenes/archivo.png"}`. Mejor PNG con fondo transparente; si el fondo es liso, se quita solo. |
| `fuente_clips` | Pie de foto de los clips (`"Título (Estudio, año)"`). Cada clip puede cambiarlo con `pie` (o quitarlo con `"pie": ""`). |
| `personaje` | `{"carpeta": "personaje", "pose": "normal", "alto": 470}`: una imagen PNG por pose; el nombre del archivo es el de la pose. Opcional. |
| `tira` | `true` (por defecto): tira de película abajo con miniaturas de los clips. `false` para quitarla. |
| `subtitulos` | `true` por defecto. `subtitulos_tam` cambia el tamaño (76). |
| `efectos` | `true` por defecto: sonidos solo en sellos, tachados, transiciones y la palabra final. `volumen_efectos` (0,35). |
| `frases` | Una por línea del guion, en orden (ver abajo). |
| `final_tiktok` | La última frase para el segundo final (mismos campos que una frase). |
| `portada` | `etiqueta` (arriba, pequeña), `linea`, `grande` (número o palabra enorme), `remate`, y una imagen: `"imagen": "clave"` o un fotograma de un clip con `"clip": "clave", "segundo": 1.5`. Con personaje, `pose`. |

## Plantilla mínima
```json
{"nombre": "mi-video", "voz": "voz", "fuente_clips": "Título (año)",
 "clips": {"escena1": "clips/escena1.mp4"},
 "frases": [
  {"titular": ["DOS PALABRAS", "OTRA LÍNEA@palabra"], "elementos": [{"tipo": "clip", "src": "escena1"}]},
  {"titular": ["COMENTA"], "elementos": [{"tipo": "palabra", "texto": "PALABRA"}]}
 ]}
```
Una entrada en `frases` por línea del guion. Todo lo demás es opcional.

## Cada frase
```json
{"titular": ["UN VILLANO", "LO PREDIJO@predijo"], "pose": "sorpresa", "transicion": "papel",
 "poses": [{"pose": "pulgar", "en": "genial"}], "subtitulos": false,
 "elementos": [ ... ]}
```
- `titular`: 1–3 líneas de 2–4 palabras. `@palabra` hace que esa línea entre cuando se oye la palabra; la primera línea, sin `@`, entra al empezar la frase. `**PALABRA**` va en la caja de color. `[]` deja el titular vacío; si la frase no tiene `titular`, se queda el anterior.
- `pose`: pose del personaje desde que empieza la frase; `poses` cambia de pose dentro de la frase.
- `transicion`: `"papel"` pasa una hoja rasgada al empezar la frase (úsala al empezar cada bloque del guion).
- `subtitulos: false`: quita los subtítulos de esa frase (por ejemplo, si la frase sale en grande).
- `titular_b`: titular solo para la versión B (la de las citas originales). En un elemento, `"versiones": ["a"]` o `["b"]` hace que salga solo en esa versión: así, si en B la cita dice otra cosa, cambias el sello o la etiqueta sin tocar la A.

## Elementos (zona central, y = 450–1280)
Campos comunes:
| Campo | Qué hace |
| --- | --- |
| `en` | Cuándo entra: una palabra de la frase (`"botas"`, `"botas#2"` para la segunda vez) o segundos desde que empieza la frase (`1.2`). Sin `en`, al empezar la frase. Las tildes y mayúsculas dan igual. |
| `hasta` | Cuándo sale (palabra o segundos). Sin `hasta`, al acabar la frase. |
| `sigue` | Número de frases más que se queda en pantalla. |
| `x`, `y` | Centro en píxeles (el vídeo es 1080×1920). Sin `x`/`y` se colocan solos. |
| `ancho` | Ancho en píxeles. |
| `giro` | Grados (positivo, a la izquierda). Sin giro, uno pequeño al azar. |
| `entra` | `pop`, `gira`, `cae`, `sube`, `desliza`, `desliza_d` o `sello`. Cada tipo tiene uno por defecto. |
| `sonido` | Efecto al entrar: `golpe`, `tachar`, `exito`, `pasa`, `clic`, `pop`, `check`… |

Tipos:
| `tipo` | Campos propios | Para qué |
| --- | --- | --- |
| `clip` | `src`, `desde` (s), `velocidad`, `pie`, `cinta`, `proporcion`, `con_cita` | Un trozo de vídeo en un marco de foto con cinta. |
| `imagen` | `src`, `pegatina` (true) | Recorte con borde blanco de pegatina. |
| `icono` | `nombre`, `color` (`acento`, `rojo`, `texto`… o #hex) | Dibujos propios: lapiz, tijeras, codigo, microfono, botas, libro, claqueta, mando, regalo, estrella, flecha, check, cruz, rayo, bombilla, corazon, reloj, bocadillo, cohete, ojo, camara, dinero, trofeo, mundo. |
| `etiqueta` | `texto`, `fondo` (`papel`, `acento`, `texto`, `periodico`), `tam` | Tira de papel con texto. |
| `sello` | `texto`, `color` (`rojo`, `acento`, `texto` o #hex), `tam` | Sello de tinta que cae de golpe («RECHAZADO», «2004»). |
| `precio` | `texto` | Etiqueta de precio. |
| `nota` | `texto` | Pósit con letra cursiva. |
| `palabra` | `texto`, `tam` | Palabra enorme en caja de color (la del final). |
| `grande` | `texto` (con `**`), `tam` | La frase en grande: cada palabra aparece cuando se oye. |
| `cuadricula` | `n`, `columnas`, `src` (miniatura opcional), `llena` (palabra en que acaba de llenarse) | Muchas tarjetas iguales que se multiplican. |
| `pasos` | `textos` (lista), `en_cada` (lista de palabras) | Tarjetas numeradas que entran una a una. |
| `tachar` | `sobre` (número del elemento de la frase, desde 0) o `x`, `y`, `ancho`, `alto` | Tachón rojo que se dibuja. |
| `rasga` | `de`, `a` (imágenes), `rasga_en` (palabra), `ancho_a` | Una imagen se rompe y aparece otra. |
| `esquema` | `icono`, `texto` | Dibujo en papel cuadriculado. |

## Ritmo
- 2–3 elementos por frase, cada uno con `en` en la palabra que lo nombra.
- Algo tiene que cambiar en cada zona al menos cada 0,6 s: lo mide `ritmo.py --por-zona`. Los elementos flotan un poco y la tira de película siempre corre, pero si una frase larga solo tiene un elemento, el centro se queda quieto: añade otro con `en`.
- Titular y subtítulos no se tocan: deja los elementos dentro de y = 450–1280. `--muestras` avisa si algo se sale o se pisa.

## Dos finales
1. La voz principal termina con el primer final. Graba aparte solo la frase del segundo.
2. `finales.py` corta la voz justo antes de la última frase y pega el otro final con 0,12 s de silencio (`--salida P/voz_tiktok`).
3. En `video.json`, `final_tiktok` es la última frase del segundo final.
4. `render.py P/video.json` y después `render.py P/video.json --final tiktok`: el segundo reutiliza el cuerpo y solo monta el final.

## Versión con citas originales (`citas.json`)
```json
[
 {"frase": 4, "clip": "originales/escena.mp4", "tramos": [[105.4, 107.6]], "texto": "Lo que dice el audio.",
  "desde": "vete", "hasta": "solo"},
 {"frase": 3, "clip": "originales/escena.mp4", "tramos": [[101.8, 104.5]], "texto": "¡Otra frase!", "despues": "cohete"}
]
```
- `frase` empieza en 1. `clip` es el clip **con audio**. `tramos`, los segundos que suenan (si hay dos, la pausa entre ellos se acorta a 0,6 s).
- `desde`/`hasta`: palabras de tu guion que sustituye la cita (sin ellas, la frase entera). `despues`: la mete detrás de esa palabra sin quitar nada.
- `texto`: lo que se oye de verdad; sale en los subtítulos.
- Para que el clip mueva los labios a la vez que suena, pon `"con_cita": true` en ese elemento `clip` (usa el clip original desde el principio de la cita).
- `citas.py … --salida P/voz_b` y `render.py P/video.json --voz voz_b --sufijo b` (el sufijo `b` es lo que activa `titular_b` y `"versiones": ["b"]`). Para ver un fotograma de la B: `render.py P/video.json --voz voz_b --sufijo b --en 12.5`.
- En la B, `en` y `@` también aceptan palabras de lo que se oye en la cita (por ejemplo, `"en": "volar"`).
- `citas.py` dice qué se oye en cada cita y avisa si un tramo corta una palabra. Si avisa de que `texto` no coincide, corrígelo: los subtítulos de la B salen de `texto`.
- **B con el final de TikTok:** `finales.py --voz P/voz_b --final final_tiktok.mp3 --texto "…" --salida P/voz_b_tiktok` y `render.py P/video.json --final tiktok --voz voz_b_tiktok --sufijo b` (reutiliza el cuerpo de la B).
