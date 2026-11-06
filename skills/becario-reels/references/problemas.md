# Problemas y soluciones

Busca el síntoma. Si no está, lee el mensaje de error entero: casi todos dicen qué hacer.

## Instalación (preparar.py)

| Síntoma | Causa y arreglo |
|---|---|
| `npm: command not found` / «no hay npm» | Falta Node.js. En la app de Claude viene instalado; en Claude Code, instala Node 18 o más nuevo (nodejs.org). |
| `ENOTFOUND registry.npmjs.org`, `403`, `ETIMEDOUT` al instalar | El entorno no tiene acceso a npm. En la app: Ajustes → Capacidades → acceso a red de la ejecución de código, al menos «gestores de paquetes». Después, nueva conversación. |
| «no hay navegador para renderizar» | preparar.py prueba: Chrome/Chromium instalado → descarga de Remotion → Chromium empaquetado en npm (@sparticuz/chromium). Si fallan los tres, no hay acceso a npm (ver arriba). En Claude Code basta con tener Google Chrome. |
| `npm ci` falla | preparar.py repite solo con `npm install`. Si también falla, el mensaje de arriba dice por qué. |
| Va muy lento la primera vez | Normal: 1–2 min instalando. Las siguientes veces en la misma carpeta, segundos. |

## Plan (resumen)

| Mensaje | Arreglo |
|---|---|
| «El plan tiene N frases y tiempos.json tiene M» | Has cambiado frases después de alinear. Vuelve a ejecutar alinear.py. |
| «no encuentro «palabra»» | Ese momento de `en` no está en la frase. Usa una palabra que sí esté (sin tildes da igual) o `inicio`. |
| «es demasiado largo» | Acorta el texto de pantalla (no el de la voz). |
| «el icono «x» no existe» | Busca el nombre en lucide.dev/icons (en inglés, con guiones). |
| «no existe el tipo de escena» | Mira los tipos en escenas.md; para una propia, `"tipo": "propia", "nombre": …`. |
| AVISO «la pantalla se queda vacía» | El primer momento llega tarde: ponlo en una palabra anterior. |

## Voz y sincronización (alinear.py)

| Síntoma | Arreglo |
|---|---|
| Los subtítulos van adelantados o atrasados en una frase | Comprueba que `texto` es exactamente lo que se oye (una palabra de más o de menos desplaza el reparto). Corrige y vuelve a alinear. |
| alinear.py da un AVISO de que una frase va mucho más rápida o lenta que el resto | Un corte entre frases está en el sitio equivocado: casi siempre, una frase partida donde la voz no hace pausa. Júntala con la de al lado y vuelve a alinear, o usa `--motor asr`, que corta por las palabras reconocidas. |
| Desfase en muchas frases | Prueba `--motor asr` (más exacto): `alinear.py --descargar-modelo` una vez (descarga ~470 MB de github.com; si la red no lo deja, se queda con el motor de sílabas, que también vale). Con asr dice cuántas palabras ha reconocido y cuántas ha usado. |
| El vídeo sale sin voz | `tiempos.json` tiene que venir de alinear.py con el audio (no con `--sin-voz`) y el plan no puede tener `"voz": false` (el resumen avisa). |
| La voz tiene música o ruido de fondo | La alineación busca pausas: pide la voz sola, sin música (la música se añade después en la app). |
| Formato de audio raro (m4a, ogg, opus, vídeo) | alinear.py lo convierte con ffmpeg; si no puede, pide un MP3 o WAV. |
| Ha quedado demasiado lento o rápido | `--tempo 1.05` acelera un 5 % sin cambiar el tono; `--pausa 0.2` recorta más los silencios. |

## Render

| Síntoma | Arreglo |
|---|---|
| Termina con «PARCIAL» | Normal en vídeos largos: lanza el mismo comando otra vez y sigue donde iba. |
| El comando se corta por tiempo antes de acabar un trozo | `--max-segundos 200` (o menos). |
| Error de memoria, el navegador se cierra | `--hilos 1` o `--hilos 2`. |
| Pesa más de 30 MB | Se recomprime solo por encima de 28 MB (`--limite-mb`). Si aun así pesa mucho: vídeo más corto o `--crf 23`. |
| Vuelve a renderizar todo tras un cambio pequeño | Es lo normal: cualquier cambio en el plan o el código (menos la portada) rehace el vídeo entero. Por eso se revisa la hoja antes. |
| Una fuente sale como Times o Arial | La ruta de `fuentes` del estilo no existe en `public/fuentes`. |
| Una imagen sale en blanco o el render falla con 404 | La ruta debe ser relativa a `public/` (`"imagenes/foto.png"`) y el archivo tiene que estar ahí. |
| Error de React en una escena propia | `node render.mjs foto <segundo>` en ese tramo para ver el error; revisa que use solo `p`, `b` y las piezas. |
| `ffmpeg` no encontrado | preparar.py usa el que trae Remotion; si falta: `pip install imageio-ffmpeg`. |

## Personaje (poses.py)

| Síntoma | Arreglo |
|---|---|
| La cabeza «salta» al cambiar de pose | Esa pose está mal medida: `poses.py ajustar <pose> anchoCabeza=… peloArriba=…` comparando con la de referencia. |
| «no encuentro la cabeza por su color» | La referencia tiene algo por encima de la cabeza o el pelo es del color del fondo: usa como referencia una pose tranquila (`--referencia normal`). |
| Halo o borde raro alrededor | El fondo de la imagen no era liso: genérala otra vez con fondo de un color, sin sombras, o pásala ya en PNG transparente. |
| Queda recortado por un lado | La imagen original corta al personaje: genérala con más margen. |

## En la app de Claude

- Los archivos que sube el usuario están en `/mnt/user-data/uploads/`; lo que le entregas, cópialo a
  `/mnt/user-data/outputs/`.
- La carpeta de la skill es de solo lectura: el proyecto siempre en otra carpeta (`~/reel`).
- Si la conversación se hace muy larga, la carpeta del proyecto sigue ahí mientras dure la sesión: continúa desde
  el último paso que funcionó en vez de empezar de cero.
