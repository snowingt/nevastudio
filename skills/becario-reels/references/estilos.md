# Estilos, subtítulos y transiciones

## Estilos de serie

`"estilo": "nube"` en el plan. Todas las escenas funcionan con todos los estilos, porque usan los colores por su
función (fondo, acento, tarjeta…) y no por su nombre.

| Estilo | Aspecto | Fondo | Acento | Letra del título | Va bien para |
|---|---|---|---|---|---|
| `apple` | suave, ultra-limpio: tarjetas blancas con sombra difusa, azul Cupertino y negro OLED | blanco slate suave | azul Apple (#0071E3) | Inter | tecnología, apps, productos, tutoriales y motion design premium |
| `nube` (por defecto) | suave: tarjetas blancas con sombra difusa y luces que se mueven | lavanda claro | índigo | Manrope | tecnología, apps, divulgación |
| `noche` | suave, oscuro | azul casi negro | verde lima | Space Grotesk | IA, programación, temas «premium» |
| `menta` | marcado: borde grueso y sombra dura, con grano | menta | rosa | Bricolage Grotesque | estilo de vida, consejos, educación |
| `limon` | marcado, muy llamativo | amarillo | azul eléctrico | Anton (condensada) | listas, retos, humor |
| `pizarra` | marcado, oscuro | verde pizarra | amarillo | Archivo Black | finanzas, estudios, datos |

Familias: **suave** entra con fundidos (`"suave"`) y **marcado** con cortes secos (`"corte"`), salvo que el plan
diga otra cosa.

## Estilo propio (colores o fuentes de marca)

Parte de uno de serie y cambia solo lo que haga falta:

```json
"estilo": {
  "base": "nube",
  "colores": { "fondo": "#EBDDC6", "fondo2": "#E2D1B5", "manchas": ["#F4E9D8", "#FFE3C9", "#FFFFFF"],
               "acento": "#FF7A1A", "acentoTexto": "#FFFFFF", "texto": "#0E1B33" },
  "fuentes": { "titulo": { "archivo": "fuentes/archivo-black-latin-400-normal.woff2", "peso": 400 } },
  "escalaTitulo": 1
}
```

Colores que se pueden cambiar (todos `#RRGGBB`):

| Color | Dónde se ve |
|---|---|
| `fondo`, `fondo2` | degradado del fondo |
| `manchas` | 3 luces que se mueven despacio por el fondo (familia suave) |
| `texto`, `suave` | texto principal y secundario sobre el fondo |
| `acento`, `acentoTexto` | palabras clave, botones, detalles, y el texto encima del acento |
| `tarjeta`, `tarjetaTexto` | tarjetas y su texto |
| `linea` | separadores y huecos vacíos |
| `oscuro`, `oscuroTexto` | paneles oscuros (código, ventanas) |
| `borde` | bordes y sombras duras (familia marcado) |
| `exito`, `error` | verde de acierto y rojo de fallo |

Reglas para que se lea bien:
- `acentoTexto` tiene que contrastar con `acento`: blanco sobre colores oscuros o intensos (azul, morado, rojo,
  verde oscuro); texto oscuro sobre amarillos, limas, naranjas y colores claros. El blanco sobre un naranja como
  #FF7A1A contrasta poco (2,6:1); si la marca lo usa así a propósito, respétalo, pero díselo al usuario.
- `texto` tiene que contrastar con `fondo`, y `tarjetaTexto` con `tarjeta`.
- El resumen avisa de cualquier pareja por debajo de 3:1.
- Si el usuario solo da un color de marca, úsalo como `acento` y deja el resto del estilo base que mejor pegue:
  si pide algo oscuro, `noche` (suave, azul noche) va con casi cualquier color; `pizarra` (verde pizarra, con
  bordes) va mejor con amarillos y cremas. Si pide algo claro, `nube` o `menta`.
- Después de cambiar colores, mira la hoja de contacto: es donde se ve si algo no contrasta.

**Fuentes** incluidas (en `public/fuentes`, licencia OFL): Anton 400, Archivo 600/800, Archivo Black 400,
Bricolage Grotesque 800, Caveat 700 (letra a mano), DM Sans 600/800, Inter 600/800, JetBrains Mono 400/700,
Manrope 600/800, Space Grotesk 700. Los archivos se llaman `fuentes/<nombre>-latin-<peso>-normal.woff2`.
Para otra fuente: copia su `.woff2` a `public/fuentes/` y pon su ruta en `fuentes`. Las condensadas (como Anton)
necesitan `"escalaTitulo": 1.1` o más.

`fuentes` admite `titulo` (una), `texto` (lista de pesos, p. ej. 600 y 800), `mano` (una) y `mono` (lista).
`grano` (0–1) es la textura de papel de la familia marcada.

## Subtítulos

`"subtitulos"` en el plan:

- **`"linea"`** (por defecto): una línea centrada en la parte de abajo, palabra a palabra; cada grupo de palabras
  clave va en una caja del color de acento. Es el estilo de la mayoría de reels que funcionan.
- **`"bloque"`**: hasta 3 líneas arriba a la izquierda, con las palabras clave en color de acento. Deja la escena
  más pequeña. Va bien con frases largas o reels de mucho texto.
- **`"no"`**: sin subtítulos (vídeos con música y textos en pantalla).

Las frases con `"sinSubtitulos": true` no los llevan (el gancho, cuando el titular ya dice lo mismo).

## Transiciones

`"transicion"` en el plan (para todas) o `"entrada"` en una frase:

- `"corte"`: cambio seco en el fotograma en que empieza la frase. El más dinámico.
- `"suave"`: fundido corto con desenfoque. Más elegante.
- `"semitono"`: puntos del color de acento que tapan la pantalla y la destapan con la escena nueva. Úsalo 1–3 veces
  por reel para marcar cambios de bloque (del gancho al desarrollo, antes del final). Más, cansa.
