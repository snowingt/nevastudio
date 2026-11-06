---
name: becario-reels
description: Crea reels y TikToks animados en vertical con código (guion, voz con subtítulos, escenas, efectos y portada). Úsala siempre que pidan un reel, TikTok, short o vídeo vertical para redes.
---

# becario-reels

Hace reels verticales animados de principio a fin: guion, voz sincronizada palabra a palabra, subtítulos con
las palabras clave resaltadas, una escena animada por frase, efectos de sonido, portada y textos para publicar.
Todo se dibuja con código (React + Remotion), así que no gasta créditos de IA de vídeo y cada reel sale distinto
según el guion. Con una sola frase del usuario («hazme un reel sobre X») basta para empezar.

## Cómo es un reel de esta skill

- 1080×1920, 30 fps, 25–60 s. Fondo con estilo, una escena por frase y nada quieto más de 0,6 s.
- **5 Efectos Obligatorios (Anti-PowerPoint)**:
  1. *Revelado con Máscara*: Los textos suben desde contenedores con `overflow: hidden` o `clip-path` con rebote elástico.
  2. *Encadenamiento Cinético*: Cada elemento entrante choca y desplaza al elemento adyacente con transferencia de momento.
  3. *Cámara Dinámica*: Paneo y zoom continuo (scale 1.0 → 1.4 → 1.0) siguiendo al protagonista visual de la escena.
  4. *Transición Morfométrica*: La tarjeta o elemento principal de la escena previa se expande a pantalla completa para crear la interfaz de la siguiente escena.
  5. *Sincronización Rítmica*: Cifras, datos y acciones visuales clavadas al compás y picos de la voz y efectos SFX.
- La voz la pone el usuario: la genera en ElevenLabs con el texto que le das (con etiquetas de emoción), la
  graba él, o el reel va sin voz (solo texto y efectos). Los subtítulos salen palabra a palabra con la voz.
- Las escenas vienen de una biblioteca de 17 tipos (titular, chat, lista, comparación, contador, test, móvil,
  imágenes con efectos, CTA…) que se rellenan con datos. Si ninguna encaja, se escribe una propia.
- 6 estilos de serie (apple, nube, noche, menta, limon, pizarra o colores y fuentes de la marca del usuario) y un personaje opcional con poses.

## Antes de empezar: el entorno

Necesita Python 3, Node 18+ y acceso a npm. En la app de Claude: Ajustes → Capacidades → «Ejecución de código y
creación de archivos» activado, con acceso a red al menos para gestores de paquetes. Si no hay navegador
instalado, preparar.py baja uno por npm.

`SKILL` en los comandos es la carpeta donde está este archivo (en la app suele ser `/mnt/skills/user/becario-reels`).

```bash
python3 SKILL/scripts/preparar.py ~/reel      # copia la plantilla, instala (1–2 min), busca navegador y ffmpeg
```

Termina con «LISTO». Si falla, mira `references/problemas.md` antes de improvisar. Un proyecto = una carpeta;
para otro reel, otra carpeta (`~/reel2`). `--actualizar` vuelve a copiar el motor sin tocar `src/datos`,
`src/propias` ni `public`.

## Flujo de trabajo

Copia esta lista y ve marcando:

```
- [ ] 1. Guion (references/guion.md) y elección de voz
- [ ] 2. Proyecto preparado (preparar.py)
- [ ] 3. plan.json con una escena por frase (references/escenas.md)
- [ ] 4. Voz: voz.py → audio del usuario → alinear.py   (o alinear.py --sin-voz)
- [ ] 5. resumen sin problemas
- [ ] 6. Hoja de contacto revisada y corregida
- [ ] 7. Vídeo renderizado + ritmo.py sin huecos
- [ ] 8. Portada + comprobación del recorte
- [ ] 9. Entrega: vídeo, portada y textos para publicar (references/publicar.md)
```

### 1. Guion

Lee `references/guion.md` y escribe 8–16 frases cortas: gancho en la primera, una idea por frase, una o dos
palabras clave por frase entre `*asteriscos*` y una llamada a la acción al final. Enséñale el guion al usuario en
el chat y pregúntale cómo quiere la voz (ElevenLabs, grabada por él o sin voz) en la misma respuesta, para no
gastar un turno solo en eso. Si no contesta o dice «tú decides», sigue con ElevenLabs.

**Si el usuario ya trae guion y audio grabado**: no escribas guion ni uses voz.py. Copia sus frases tal cual en
`texto`, una por frase del plan (solo añade los `*asteriscos*`), y alinea. Con una voz ya grabada, una frase solo se
puede partir en dos escenas donde la voz hace una pausa; si no, déjala entera.

### 2. Proyecto

`python3 SKILL/scripts/preparar.py ~/reel` (puedes lanzarlo mientras escribes el plan).

Los comandos de los pasos siguientes se lanzan desde la carpeta del proyecto: empieza cada uno con `cd ~/reel &&`
(en muchos entornos cada comando arranca en otra carpeta).

### 3. Plan

Escribe `~/reel/src/datos/plan.json` desde cero (no edites el de ejemplo). Lee antes `references/escenas.md` (qué
escenas hay, cómo se ven, sus campos y cómo se sincronizan). Estilos de serie: `apple` (ultra-limpio, estética Cupertino), `nube` (claro y suave, por
defecto), `noche` (oscuro y suave), `menta` (claro, con bordes), `limon` (amarillo, muy llamativo) y `pizarra`
(oscuro, con bordes); para elegir bien o usar los colores de una marca, `references/estilos.md`. Forma mínima:

```json
{
  "titulo": "Reels con código",
  "estilo": "nube",
  "subtitulos": "linea",
  "frases": [
    {
      "texto": "Esta skill hace *reels enteros* con una frase.",
      "emocion": "[excited]",
      "sinSubtitulos": true,
      "escena": { "tipo": "titular", "texto": "Reels enteros / *con una frase*", "icono": "clapperboard", "en": ["reels"] }
    },
    {
      "texto": "Le pides *una idea* y escribe el reel *entero.*",
      "emocion": "[confident]",
      "escena": { "tipo": "chat", "mensaje": "haz un reel sobre café", "en": ["pides", "idea", "escribe", "reel", "entero"] }
    }
  ],
  "portada": { "etiqueta": "IA", "lineas": ["1 FRASE", "*1 REEL*"], "icono": "clapperboard" }
}
```

- `texto` es exactamente lo que dice la voz (los subtítulos salen de aquí). Si una palabra se pronuncia mal,
  pon la versión para la voz en `voz` («Claude» → «Clod») y deja `texto` bien escrito.
- `escena.en` dice en qué palabra entra cada elemento de la escena. Esto es lo que hace que el vídeo parezca
  editado a mano: que cada cosa aparezca justo cuando se nombra.
- Imágenes que pase el usuario: cópialas a `~/reel/public/imagenes/` y úsalas como `"imagenes/archivo.png"`.
- Todo texto que ya está en pantalla no lleva subtítulos: `"sinSubtitulos": true` en el gancho, en cualquier
  `titular` que diga lo mismo que la voz y en la `cta`.
- El tamaño de un titular y del título de la portada lo decide su línea más larga: pártelos con `/` en líneas
  cortas (≤14 letras) para que salgan grandes. El resumen avisa cuando salen pequeños.

### 4. Voz

- **ElevenLabs** (lo normal): `python3 SKILL/scripts/voz.py --proyecto ~/reel` saca el texto con etiquetas y los
  pasos. Pásaselo al usuario tal cual (también queda en `salida/voz.txt`) y espera su MP3.
- **Que la grabe el usuario**: igual, con `--sin-etiquetas` (texto limpio y consejos para grabar con el móvil).
- Con el audio: `python3 SKILL/scripts/alinear.py AUDIO --proyecto ~/reel`. Normaliza el volumen, recorta las
  pausas largas y calcula cuándo se dice cada palabra. Lee lo que imprime: si una frase sale con un AVISO de ritmo
  raro, su principio o su final está en la frase de al lado (casi siempre, una frase partida donde la voz no para:
  júntala). Si el usuario cambió alguna frase al grabar, cambia el `texto` del plan para que coincida.
- **Sin voz**: `alinear.py --sin-voz --proyecto ~/reel`. Sirve para reels de solo texto y para enseñar un borrador
  mientras llega la voz. Ese vídeo solo lleva los efectos de sonido, muy bajos: dile al usuario que le ponga
  música en la app al publicarlo. Cuando tenga la voz, basta con alinear con el audio y volver a renderizar.
- Cada vez que cambies el `texto` de una frase hay que volver a alinear (el resumen lo detecta y no deja renderizar).

### 5. Comprobar el plan

```bash
cd ~/reel && node render.mjs resumen
```

Enseña cada escena con sus momentos, una lista de PROBLEMAS (campos que faltan, textos que no caben, palabras de
`en` que no están en la frase, iconos que no existen, frases cambiadas desde que se alineó…) y otra de AVISOS
(títulos que saldrán pequeños, escenas que tardan en enseñar algo, elementos que apenas se ven, colores con poco
contraste). Arregla todos los problemas (`video` no renderiza con problemas) y casi todos los avisos.

### 6. Mirar antes de renderizar

```bash
cd ~/reel && node render.mjs fotos          # salida/hoja.png: mitad, momentos y final de cada escena (≈30 s)
cd ~/reel && node render.mjs foto 2.5 12    # fotogramas sueltos a tamaño completo (≈1 s cada uno)
```

Abre la hoja y mírala entera, de verdad: textos cortados o tapados, escenas vacías demasiado rato, elementos
que se pisan con los subtítulos o el personaje, colores sin contraste. La hoja es pequeña: mira siempre a tamaño
completo (`foto`) el final del gancho, el final de cada titular y cualquier texto que dudes si se lee. Corrige el
plan y repite. Es mucho más barato que descubrirlo en el vídeo.

### 7. Vídeo

```bash
cd ~/reel && node render.mjs video          # salida/reel.mp4 (≈5 s de render por cada segundo de vídeo)
```

Renderiza por trozos y se para solo antes de los ~4,5 min para no chocar con el límite de tiempo de un comando:
si termina con «PARCIAL», lánzalo otra vez y sigue donde iba. Cualquier cambio en el plan o en el código (menos
la portada) obliga a renderizarlo entero otra vez, así que deja el vídeo para cuando la hoja esté bien. Con
`--borrador` sale a mitad de resolución y mucho más rápido (para enseñar un avance). Si pasa de 28 MB lo
recomprime solo (la app no deja descargar archivos de más de 30 MB).

Después mide el ritmo:

```bash
python3 SKILL/scripts/ritmo.py ~/reel/salida/reel.mp4 --tiempos ~/reel/src/datos/tiempos.json
```

Si avisa de huecos (más de 0,6 s sin que cambie nada), lee `references/ritmo.md`, añade movimiento en esas
frases y vuelve a renderizar.

### 8. Portada

Rellena `portada` en el plan y `cd ~/reel && node render.mjs portada`. Mira `salida/portada_check.png`: enseña la
portada entera, el recorte 3:4 que usa la cuadrícula del perfil de Instagram y la miniatura pequeña. El título tiene
que leerse en las tres. Cambiar la portada no obliga a renderizar el vídeo otra vez.

### 9. Entregar

Dale al usuario `salida/reel.mp4` y `salida/portada.png` (en la app de Claude, cópialos a
`/mnt/user-data/outputs/`) y, en el chat, el título y la descripción para Instagram y TikTok siguiendo
`references/publicar.md`. Cuéntale en dos líneas qué has hecho y qué podría cambiar si quiere otra versión.

## Lo que hace que un reel funcione

Estas reglas salen de analizar fotograma a fotograma reels que funcionan. Explican la mayoría de las diferencias
entre un vídeo que se ve entero y uno que se pasa.

1. **El gancho manda.** La primera frase y su titular deciden si alguien se queda. Concreta, con algo
   sorprendente o útil, en letra grande (líneas cortas) y sin subtítulos, porque el texto ya está en pantalla.
2. **Nada quieto más de 0,6 s.** Cada escena tiene varios momentos; repártelos por la frase (`en`). ritmo.py lo mide.
3. **Una frase, una escena, una idea.** Si una frase necesita dos escenas, son dos frases.
4. **Lo que se dice, se ve.** Los elementos entran con su palabra; las palabras clave van en caja de color.
5. **Textos de pantalla cortos.** Se leen en un segundo. La validación avisa cuando algo no cabe.
6. **Variedad.** No repitas el mismo tipo de escena más de dos veces seguidas; alterna tarjetas, apps e imágenes.
7. **Final con acción.** La última frase pide algo concreto («Comenta X y te lo mando», o «Guarda este reel» si
   no hay nada que mandar): escena `cta`.
8. **Honestidad.** El gancho no promete lo que el vídeo no da. Las cifras y datos, reales y comprobados.

## Más allá de la biblioteca

- **Escena propia**: cuando ninguna escena encaja, copia `src/propias/Ejemplo.tsx`, regístrala en
  `src/propias/index.ts` y úsala con `"tipo": "propia", "nombre": "MiEscena"`. Detalles en `references/escenas.md`.
- **Personaje con poses** (mascota o avatar del usuario): `references/personaje.md`.
- **Colores y fuentes de marca**: `references/estilos.md`.

## Referencias (léelas cuando toque)

| Archivo | Cuándo |
|---|---|
| `references/guion.md` | Siempre, antes de escribir el guion |
| `references/escenas.md` | Siempre, antes de escribir el plan |
| `references/estilos.md` | Al elegir estilo, colores de marca, subtítulos o transiciones |
| `references/ritmo.md` | Si ritmo.py avisa de huecos o la hoja se ve estática |
| `references/personaje.md` | Si el usuario tiene personaje o quiere uno |
| `references/publicar.md` | Al hacer la portada y los textos para publicar |
| `references/problemas.md` | Cuando algo falla (instalación, render, voz, tamaño) |

## Licencia de Remotion

El motor de vídeo es Remotion: gratis para particulares, autónomos y empresas de hasta 3 personas. Una empresa
más grande necesita su licencia de empresa (remotion.dev/license). Si el usuario habla en nombre de una empresa
grande, díselo una vez.
