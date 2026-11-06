# Portada y textos para publicar

## Portada

Se rellena en `plan.json`:

```json
"portada": {
  "etiqueta": "TRUCOS",
  "lineas": ["3 TRUCOS", "*DEL SÚPER*", "QUE NADIE USA"],
  "icono": "shopping-cart",
  "pegatina": "−50 € al mes",
  "pose": "sorpresa",
  "oscura": false
}
```

| Campo | |
|---|---|
| `lineas` | 1–4 líneas; la primera sale enorme y las demás más pequeñas. `*así*` va en color de acento. La línea más larga decide el tamaño de todo el título: 10–12 letras por línea como mucho (el resumen avisa si te pasas), para que se lea en la miniatura del perfil. |
| `etiqueta` | píldora pequeña encima del título (tema o serie). |
| `icono` o `imagenes` | un icono grande o hasta 4 imágenes en abanico debajo del título. |
| `pegatina` | etiqueta inclinada del color de acento (un dato, un precio, «gratis»). |
| `pose` | el personaje abajo a la izquierda (si hay poses). En fondos oscuros lleva una luz detrás para que no parezca recortado. |
| `oscura` | true: fondo oscuro con el texto claro, para que en la cuadrícula se distinga de la anterior. Solo en estilos claros (en uno oscuro no hace nada). |

`node render.mjs portada` crea `salida/portada.png` (1080×1920) y `salida/portada_check.png` con tres vistas:
la portada entera, el recorte 3:4 que enseña la cuadrícula del perfil de Instagram (solo la franja central, de
y=240 a y=1680) y la miniatura pequeña. El título y la cara tienen que verse en las tres.

Ideas que funcionan: el número o la promesa del gancho en grande, una sola palabra en color de acento, el personaje
con cara de sorpresa mirando al título. Alterna fondo claro y oscuro entre reels para que la cuadrícula no sea monótona.

## Textos

Dáselos al usuario en el chat, listos para copiar, en bloques separados.

**Instagram (descripción):**
- La primera línea es lo único que se ve sin pulsar «más»: repite o completa el gancho (≤125 caracteres).
- 3–6 líneas cortas con lo que aprende quien lo vea, con algún emoji si encaja con la cuenta.
- La llamada a la acción del vídeo, igual («Comenta LISTA y te la mando por privado»).
- 3–5 hashtags del tema, mezclando generales y concretos. No 30.

**TikTok (descripción):**
- Empieza con las palabras que alguien buscaría («trucos para ahorrar en el súper»): TikTok funciona mucho como
  buscador.
- 1–3 líneas, la llamada a la acción y 3–5 hashtags.

**Título corto** (para la portada en TikTok o para YouTube Shorts, si lo sube allí): ≤60 caracteres, con la promesa.

## Al subirlo

- Sube `reel.mp4` tal cual (1080×1920, H.264, AAC): no hace falta convertirlo.
- Instagram: «Editar portada» → «Añadir desde la galería» → `portada.png`.
- TikTok: «Editar portada» → sube `portada.png` desde la galería antes de publicar (después ya no se puede cambiar).
- Si quiere música, que la añada en la app a volumen bajo: la voz tiene que seguir mandando.
- Si la voz está hecha con IA, que active la etiqueta de contenido generado con IA al publicar (las dos apps la
  piden para voces sintéticas realistas).

## «Comenta PALABRA» con respuesta automática

- **Instagram**: herramientas como ManyChat (socio oficial de Meta) mandan un mensaje privado a quien comente una
  palabra. Se configura una vez por palabra y funciona solo.
- **TikTok**: no deja escribir por privado a quien comenta, y su API de mensajes no está disponible en el Espacio
  Económico Europeo, Suiza ni Reino Unido. Alternativa: enlace en la bio (una cuenta de empresa, que es gratis,
  permite ponerlo sin llegar a 1.000 seguidores), un comentario fijado que lleve a la bio, o pedir que escriban la
  palabra por mensaje y contestar a mano.
- Antes de publicar, comprueba que lo que se promete existe y está listo para enviar.
