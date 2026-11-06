# Personaje con poses (opcional)

Un personaje fijo (mascota, avatar o caricatura del creador) que reacciona a lo que se dice da mucha
personalidad a una cuenta y hace que los reels se reconozcan al instante. Es opcional: sin poses, el reel no
lleva personaje y las escenas ocupan más pantalla.

## Cómo queda

Abajo a la izquierda, de cintura para arriba, con la cabeza siempre del mismo tamaño y en el mismo sitio aunque
cambie la pose (por eso se mide la cabeza de cada imagen). Respira y se balancea muy poco: tranquilo, para no
distraer. Con personaje, los subtítulos suben un poco y las escenas se encajan encima.

## Imágenes que hacen falta

- El **mismo personaje** y el **mismo dibujo** en todas: colores, proporciones, grosor de línea.
- **De cintura para arriba**, mirando a cámara, centrado, sin cortar la cabeza ni las manos.
- **Fondo liso de un solo color**, sin sombras ni degradados (o PNG con fondo transparente). Mejor un color
  parecido al fondo del estilo que vayas a usar: si hay algún resto en el borde, no se nota.
- Al menos **1000 px de alto**. Nada de capturas pequeñas ampliadas.
- 4–6 poses bastan para empezar.

Poses que más se usan (el nombre es el que irá en el plan):

| Pose | Para |
|---|---|
| `normal` | por defecto, hablando tranquilo (será la de referencia) |
| `presenta` | gancho, «mira esto» (mano abierta hacia un lado) |
| `senala_arriba` / `senala_abajo` | señalar lo que aparece en pantalla o el CTA |
| `piensa` | preguntas, dudas |
| `sorpresa` | datos que impresionan |
| `celebra` | logros, final |
| `pulgar` | confirmación, «así de fácil» |
| `brazos_cruzados` / `niega_dedo` | objeciones, «no hagas esto» |
| `uno` / `dos` / `tres` | contar con los dedos en listas |

Si el usuario no tiene las imágenes, dale este texto para generarlas con su IA de imágenes (adjuntando una imagen
del personaje como referencia), una vez por pose:

> Usa exactamente este personaje: mismo dibujo, colores, peinado, ropa y proporciones. Dibújalo de cintura para
> arriba, mirando a cámara y centrado, sobre un fondo liso de un solo color #EBDDC6, sin sombras ni degradados.
> Pose: [describe la pose, p. ej. «señalando hacia arriba con la mano derecha, sonriendo»]. Formato vertical.

## Prepararlas

```bash
python3 SKILL/scripts/poses.py --proyecto ~/reel recortar carpeta_con_poses/      # nombre de la pose = nombre del archivo
python3 SKILL/scripts/poses.py --proyecto ~/reel recortar normal normal.png celebra celebra.png
```

Quita el fondo con un borde fino (sin halo claro alrededor de la línea), recorta, alarga la imagen por abajo si
llega cortada y mide la cabeza. La cabeza se reconoce por el color de lo más alto de la pose de referencia
(`normal`, o la primera): por eso la referencia debe ser una pose tranquila, sin los brazos por encima de la cabeza.

Comprueba en la hoja de contacto que al cambiar de pose la cabeza no salta. Si una sale grande, pequeña o movida:

```bash
python3 SKILL/scripts/poses.py --proyecto ~/reel ajustar celebra anchoCabeza=380 peloArriba=20
```

(`cabeza` es la x del centro de la cabeza de 0 a 1; `anchoCabeza` y `peloArriba`, en píxeles de esa imagen.)
`medir` vuelve a medirlas todas y `quitar nombre` borra una.

## Usarlas en el plan

```json
"personaje": true,
"frases": [
  { "texto": "…", "poses": [["inicio", "presenta"]], "escena": { … } },
  { "texto": "¿Pensarás que es *difícil?*", "poses": [["difícil", "piensa"]], "escena": { … } }
]
```

- `poses` es una lista de `[momento, pose]` (momentos como en escenas.md). La pose se mantiene hasta el siguiente
  cambio, aunque sea en otra frase.
- 0–2 cambios por frase, en la palabra que justifica el gesto. Cambios más seguidos de medio segundo marean.
- Si ninguna frase dice pose, sale la de referencia todo el vídeo.
- `"personaje": false` lo quita de un reel aunque haya poses.
- Para la portada: `"portada": { …, "pose": "sorpresa" }`.
