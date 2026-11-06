# Escenas

Cada frase del guion lleva una escena. Aquí está cómo se escriben en `plan.json`, el catálogo de las 17 que trae la
plantilla y cómo hacer una propia cuando ninguna encaja.

## Índice
1. Cómo se escribe una frase en el plan
2. Momentos: cuándo entra cada cosa
3. Qué escena usar para cada frase
4. Catálogo (titular, chat, editor, movil, contador, cifras, ficha, lista, pasos, comparacion, tachado, objecion,
   pregunta, barras, imagen, galeria, cta)
5. Iconos, imágenes y sonidos
6. Escenas propias

## 1. Cómo se escribe una frase en el plan

```json
{
  "texto": "No es una *IA de vídeo:* es *código.*",
  "voz": "No es una IA de vídeo: es código.",
  "emocion": "[confident]",
  "entrada": "semitono",
  "sinSubtitulos": false,
  "poses": [["inicio", "piensa"], ["código", "celebra"]],
  "sonidos": [["código", "ding", 0.3]],
  "escena": { "tipo": "comparacion", "en": ["IA", "código", "código+12"], "izquierda": { "titulo": "IA de vídeo" }, "derecha": { "titulo": "Código" } }
}
```

| Campo | Para qué |
|---|---|
| `texto` | Lo que dice la voz, con las palabras clave entre `*asteriscos*`. Obligatorio. |
| `voz` | Cómo se pronuncia, si no coincide con `texto` (solo para generar la voz). |
| `emocion` | Etiqueta de ElevenLabs para esta frase (`[excited]`, `[curious]`…). |
| `escena` | `tipo` + sus campos + `en` (momentos). Obligatorio. |
| `entrada` | Cómo entra la escena: `"corte"` (seco), `"suave"` (fundido con desenfoque) o `"semitono"` (puntos que tapan y destapan). Si no se pone, la del estilo. Usa `semitono` 1–3 veces por reel para marcar cambios de bloque. |
| `sinSubtitulos` | `true` cuando el texto ya está en pantalla (el titular del gancho). |
| `poses` | Cambios de pose del personaje: `[momento, pose]` (ver personaje.md). |
| `sonidos` | Efectos extra: `[momento, sonido, volumen 0–1]`. Las escenas ya ponen los suyos. |

Campos generales del plan: `titulo` (nombre del reel; sale en la escena `editor`), `estilo`, `subtitulos`
(`"linea"`, `"bloque"` o `"no"`), `transicion` (entrada por defecto), `personaje` (true/false), `voz` (false si
no hay voz), `frases` y `portada` (ver publicar.md). Estilos y subtítulos: estilos.md.

## 2. Momentos: cuándo entra cada cosa

Cada escena tiene un número fijo de momentos (los elementos que van entrando). `en` dice cuándo entra cada uno,
en orden. Formas de escribir un momento:

| Momento | Significa |
|---|---|
| `"palabra"` | cuando se dice esa palabra (sin tildes ni signos; primero busca la palabra exacta y si no, una que empiece así: `"anim"` vale para «animación»). Las cifras, sin puntos ni símbolos: «1.500 €» es `"1500"` y «80 %» es `"80"` |
| `"palabra#2"` | la segunda vez que sale esa palabra en la frase |
| `"palabra+6"` / `"palabra-4"` | 6 fotogramas después / 4 antes (30 fotogramas = 1 s). Se combinan: `"palabra#2+6"` |
| `"inicio"` / `"fin"` | principio o final de la escena |
| `12` (número) | fotogramas desde que empieza la escena |

- Las palabras salen un pelín antes de oírse (4 fotogramas), así el ojo llega a tiempo.
- Si `en` trae menos momentos de los que usa la escena, el resto se reparte solo hasta el final de la escena; si
  no hay `en`, se reparte todo. Funciona, pero sincronizar a mano con las palabras clave queda mucho mejor.
- El primer momento debe caer pronto (en las primeras palabras): el resumen avisa si la escena tarda más de 0,8 s
  en enseñar algo.
- Reparte los momentos por toda la frase: si todos caen al principio, el final se queda quieto (ritmo.py lo pilla).
  Pero el último no puede caer en la última palabra si la escena cambia justo después: no daría tiempo a verlo (el
  resumen también avisa).
- Si das más momentos de los que usa la escena, sobran (el resumen lo dice).

## 3. Qué escena usar para cada frase

| La frase… | Escena |
|---|---|
| es el gancho, un título de bloque o una pregunta al aire | `titular` |
| dice un número que impresiona | `contador` (uno) · `cifras` (2–3) · `barras` (comparar cantidades) |
| enumera cosas | `lista` (checklist) · `pasos` (orden 1-2-3) |
| compara dos opciones | `comparacion` |
| corrige una idea («no es X, es Y») | `tachado` |
| se adelanta a una duda («¿pensarás que…?») | `objecion` |
| plantea un test o adivinanza | `pregunta` |
| describe algo con datos (precio, tiempo, formato) | `ficha` |
| habla de una app, una web o un resultado en el móvil | `movil` |
| enseña cómo se le pide algo a una IA | `chat` |
| enseña una foto o ilustración | `imagen` (una) · `galeria` (varias) |
| cuenta que el vídeo está hecho con código | `editor` |
| pide la acción final | `cta` |

No repitas el mismo tipo más de dos veces seguidas. Dos escenas seguidas del mismo tipo `chat` o `editor` se unen
(la segunda continúa la primera sin volver a entrar).

## 4. Catálogo

Los límites de letras están para que el texto se lea en pantalla; la validación avisa si te pasas.

### titular (1 momento)
Título grande que se escribe palabra a palabra al ritmo de la voz. Las palabras entre asteriscos salen en letra a
mano y color de acento. Debajo, un icono grande o un abanico de imágenes.

| Campo | |
|---|---|
| `texto` | obligatorio, ≤90. Usa `/` para partir líneas (≤4 líneas de ≤28 letras). Las palabras deben ser las que dice la voz, en el mismo orden, para que salgan sincronizadas. |
| `etiqueta` | ≤24, encima del título (`"¿SABÍAS QUE…?"`, `"GRATIS"`). `etiquetaGrande: false` para que no entre grande desde el centro. |
| `icono` | icono grande debajo |
| `imagenes` | ≤4 imágenes en abanico debajo (en vez del icono) |

Momento: 1 = entra el icono o las imágenes.

**El tamaño lo decide la línea más larga.** «¿Das vueltas en la cama?» en una línea sale pequeño; partido en
«¿Das vueltas / en la cama?» sale mucho más grande. Líneas de 14 letras o menos (el resumen avisa a partir de 18).
Si la voz dice lo mismo que el titular, ponle `"sinSubtitulos": true` a esa frase, también a mitad del reel.

```json
{ "tipo": "titular", "etiqueta": "¿SABÍAS QUE…?", "texto": "Tu móvil traduce / *en directo*", "icono": "languages", "en": ["traduce"] }
```

### chat (5 momentos)
Ventana de chat con una IA: se escribe un mensaje, se envía, la IA responde con código que se va escribiendo y
aparece una vista previa en un móvil.

Campos (todos opcionales): `mensaje` (≤38, lo que se escribe), `titulo` (≤20, nombre del asistente, por defecto
«Claude»), `saludo` (≤28), `respuesta` (≤26), `archivo` (nombre del archivo de código), `movil`
(`{ "titulo": "Café", "subtitulo": "recién hecho", "icono": "coffee" }`), `pildora` (≤34, etiqueta final),
`anotacion` (≤16, nota a mano que señala el mensaje).

Momentos: 1 empieza a escribir · 2 envía · 3 responde · 4 sale el móvil · 5 sale la píldora.

### editor (4 momentos)
Zoom hacia atrás desde la pantalla que revela el propio reel dentro de un editor de vídeo con sus pistas.
Campos: `hecho` (≤24, píldora; por defecto «hecho con código»), `archivo` (≤24), `palabras` (≤4 chips que vuelan a
la pista de subtítulos), `sonidos` (≤3 chips a la pista de sonidos).
Momentos: 1 zoom · 2 píldora · 3 palabras · 4 sonidos.

### movil (3 momentos)
Un móvil con una pantalla, una pegatina y, si quieres, un contador.
Campos: `titulo` (obligatorio, ≤24), `subtitulo` (≤18), `icono`, `pegatina` (≤12),
`contador` (`{ "desde": 0, "hasta": 12500, "etiqueta": "visitas" }`).
Momentos: 1 entra el móvil · 2 contenido y contador · 3 pegatina. En estilos oscuros el móvil se distingue poco
del fondo: ahí luce más en `nube`, `menta` o `limon`.

### contador (2 momentos)
Tarjeta con un número grande que cuenta hasta el valor y da un golpe al llegar.
Se ve: la etiqueta arriba y el número enorme debajo, con una barra que se llena.
Campos: `valor` (número, obligatorio), `etiqueta` (obligatorio; mejor ≤28 letras, para que quepa en una línea),
`desde` (el número del que parte la cuenta, hacia arriba o hacia abajo: `"desde": 25, "valor": 18` baja de 25 a 18;
sin `desde`, el número sale fijo), `prefijo` / `sufijo` (`"€"`, `" %"`, `" h"`, `" °C"`), `icono`, `llama` (true:
una llama que se enciende y se apaga, para «quemar» o «gastar»), `destacar` (por defecto true: el número pasa al
color de acento al final).
Momentos: 1 entra y empieza a contar · 2 llega al valor (golpe).

```json
{ "tipo": "contador", "valor": 50, "desde": 0, "sufijo": " €", "etiqueta": "ahorras al mes", "icono": "piggy-bank", "en": ["trucos", "mes"] }
```

### cifras (1–3 momentos)
Hasta 3 filas con un número grande cada una y su etiqueta a mano.
`filas`: `[{ "valor": 17, "etiqueta": "escenas", "detalle": "≤30 letras", "desde": 0, "prefijo": "", "sufijo": "", "destacar": false }]`
(`etiqueta` ≤14). Sin `detalle`, debajo de la etiqueta salen unas barritas animadas. Momentos: uno por fila.

### ficha (1–4 momentos)
Tarjeta de datos: título con icono, etiqueta opcional y hasta 4 filas «etiqueta → valor».
Campos: `titulo` (≤18), `icono`, `etiqueta` (≤14), `filas`: `[["formato", "1080×1920"], ["coste", 0, true]]`
(el `true` resalta la fila en color de acento). Momentos: uno por fila. Es una tarjeta compacta: con 3–4 filas
llena mejor la pantalla que con 1–2.

### lista (2–5 momentos)
Checklist: cada elemento entra y se marca. `titulo` (≤22, opcional), `items`: textos o
`{ "texto": "≤30 letras", "icono": "mic" }` (2–5). Momentos: uno por elemento.

### pasos (2–4 momentos)
Pasos numerados unidos por flechas. `pasos`: textos o `{ "texto": "≤34 letras", "icono": "download" }` (2–4).
Momentos: uno por paso.

### comparacion (3 momentos)
Dos tarjetas con «VS»; la ganadora se marca y la otra se apaga.
Campos: `izquierda` y `derecha` (`{ "titulo": "≤16", "texto": "≤50", "icono": "film" }`), `ganador`:
`"derecha"` (por defecto), `"izquierda"` o `"ninguno"`.
Momentos: 1 izquierda · 2 derecha · 3 veredicto.

### tachado (2 momentos)
«No es X: es Y». Se ve una tarjeta con X en letra grande desde el principio; se tacha con una cruz roja, sube
apagado y debajo entra Y, grande y en color de acento.
Campos: `antes` (≤22), `despues` (≤18), `icono` o `imagen` (arriba en la tarjeta, opcional), `modo`: `"texto"`
(por defecto) o `"codigo"` (Y sale como código, `</> Y`).
Momentos: 1 se tacha · 2 aparece lo nuevo.

### objecion (2 momentos)
Bocadillo «¿Pensarás que… *texto*?» con interrogantes, y la respuesta en una píldora.
Campos: `texto` (≤60, sin «?», se añade solo), `respuesta` (≤30), `numero` (≤12, píldora arriba, p. ej. «Mito 1»).
Momentos: 1 bocadillo · 2 respuesta.

### pregunta (3 momentos)
Test: pregunta, opciones (A, B, C…) y se revela la buena en verde.
Campos: `pregunta` (≤60), `opciones` (2–4, ≤28 letras), `correcta` (índice desde 0; por defecto 0).
Momentos: 1 pregunta · 2 opciones · 3 solución. Pon el 3 en la palabra que da la respuesta.

### barras (2–5 momentos)
Gráfico de barras que crecen una a una. `barras`: `[{ "etiqueta": "≤12", "valor": 120 }]` (2–5), `titulo` (≤26),
`unidad` (≤4, `"%"`, `"€"`), `destacar` (índice de la barra en color de acento). Momentos: uno por barra.

### imagen (2 momentos)
Una imagen grande con marco y efectos animados con código.
Campos: `imagen` (obligatorio, `"imagenes/x.png"`), `formato`: `"horizontal"` (3:2, por defecto), `"cuadrada"` o
`"vertical"`, `texto` (≤34, píldora), `etiqueta` (≤22), `efectos` (lista): `agua` (ondula la imagen), `causticas`
(reflejos de agua), `estrellas`, `haz` (haz de faro; posición con `"haz": [0.3, 0.3]`), `burbujas`, `rayos` (luz),
`cine` (barras de cine y subtítulo), `flotar`; `peces`: `{ "imagen": "imagenes/pez.png", "n": 2 }` (PNG con fondo
transparente del animal visto desde arriba; nadan por encima).
Momentos: 1 entra la imagen · 2 texto o etiqueta.

### galeria (2 momentos)
Varias imágenes (2–6). `modo`: `"abanico"` (entran juntas y se abren en el momento 2, por defecto), `"orbita"`
(giran alrededor de un icono: `centro`) o `"rejilla"` (cuadrícula; `destacar`: índice que se resalta en el 2).
`etiqueta` (≤30). Momentos: 1 entran · 2 se abren o se resalta una.

### cta (3 momentos)
La llamada a la acción: «Comenta PALABRA» con la palabra escribiéndose letra a letra, texto a mano, un sobre que
sale volando, confeti e iconos que saltan por turnos hasta el final (para que no se quede quieto).
Campos: `palabra` (≤12, obligatorio; mejor sin tildes), `verbo` (≤14, por defecto «Comenta»), `texto` (≤50, a mano;
`/` parte líneas), `iconos` (≤5; por defecto mensaje, enviar, regalo, lista y check).
Momentos: 1 la palabra · 2 el texto · 3 iconos, sobre y confeti. Lleva `"sinSubtitulos": true`.

```json
{ "tipo": "cta", "palabra": "LISTA", "texto": "y te mando / todos los trucos", "en": ["LISTA", "mando", "trucos"] }
{ "tipo": "cta", "verbo": "Guarda", "palabra": "ESTE REEL", "texto": "y pruébalo / esta noche", "iconos": ["bookmark", "moon", "bed", "star", "check"], "en": ["Guarda", "pruébalo", "noche"] }
{ "tipo": "cta", "verbo": "Sígueme", "palabra": "PARTE 2", "texto": "mañana, / el truco final", "iconos": ["user-plus", "bell", "sparkles", "play", "check"], "en": ["Sígueme", "mañana", "final"] }
```

## 5. Iconos, imágenes y sonidos

- **Iconos**: cualquier icono de Lucide por su nombre en inglés con guiones (`"rocket"`, `"shopping-cart"`,
  `"piggy-bank"`, `"brain"`). Lista en lucide.dev/icons. Si no existe, el resumen lo dice.
- **Imágenes**: van en `public/imagenes/` y se escriben como `"imagenes/archivo.png"` (png, jpg o webp). Las del
  usuario, cópialas ahí. Si un reel necesita imágenes que el usuario no tiene, pídeselas o usa escenas sin imagen:
  no inventes rutas.
- **Sonidos** de la plantilla: `pop`, `ding`, `exito`, `campana`, `tecla`, `tic`, `clic`, `whoosh`, `swoosh`,
  `papel`, `burbuja`, `golpe`, `negacion`, `puff`, `cristal`, `proyector`, `subida`. Volumen 0,2–0,45 (la voz manda).

## 6. Escenas propias

Cuando ninguna escena encaja (un mapa, un reloj, un juego, un antes/después con dibujo…), escribe una en React:

1. Copia `src/propias/Ejemplo.tsx` a `src/propias/MiEscena.tsx` y cambia el nombre del componente y de la
   definición.
2. Regístrala en `src/propias/index.ts`: `PROPIAS = { Ejemplo: ejemplo, MiEscena: miEscena }`.
3. Úsala en el plan: `"escena": { "tipo": "propia", "nombre": "MiEscena", "en": ["…"], …tus campos }`.
4. `node render.mjs foto <segundo>` para verla de cerca mientras la ajustas.

Reglas para que encaje con el resto:
- Recibe `p` (tus campos), `b` (fotograma de cada momento, relativo al inicio de la escena), `dur`, `palabras` e `i`.
  Declara cuántos momentos usa en `momentos` y sus sonidos en `sonidos`.
- Dibuja dentro del lienzo: x 60–1020, y 210–1070 (centro 540, 640). El motor lo escala si hay personaje o
  subtítulos en bloque.
- Usa los colores por su uso (`C.acento`, `C.tarjeta`, `C.texto`, `C.oscuro`… de `../motor/actual`) y las fuentes
  `F.titulo`, `F.texto`, `F.mano`, `F.mono` (de `../motor/estilos`): así funciona con cualquier estilo.
- Piezas listas en `src/piezas/basicas.tsx` (Tarjeta, Pildora, Icono, Chip, Anotacion, Tachon, Marca, Confeti,
  Onda, Destello, LineaPuntos…), `imagenes.tsx` (ImagenCard y efectos) y `ventanas.tsx` (VentanaChat, Editor,
  MovilVista, CodigoStream). Animaciones en `src/motor/anim.ts` (usePop, useFlota, lerp, bump).
- Que siempre se mueva algo: un elemento nuevo como mucho cada 0,6 s.
- Si algo falla al renderizar, el error de React sale en la consola de `node render.mjs foto`.
