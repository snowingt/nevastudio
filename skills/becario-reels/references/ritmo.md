# Ritmo

## La regla

En los reels que retienen, nunca pasan más de 0,6 s sin que algo nuevo entre o cambie en pantalla: una palabra
del subtítulo, una tarjeta, un icono, un número que cuenta, un cambio de pose. La vista se engancha a lo que se
mueve; un tramo quieto es el momento en que el pulgar desliza.

## Cómo se mide

```bash
python3 SKILL/scripts/ritmo.py ~/reel/salida/reel.mp4 --tiempos ~/reel/src/datos/tiempos.json
```

Compara cada fotograma con los anteriores, por zonas de la pantalla y por baldosas pequeñas, y cuenta como
«evento» cualquier cambio que se vea (no la respiración del personaje ni las luces lentas del fondo). Da:

- **fotogramas quietos %**: lo normal está entre el 10 % y el 35 %.
- **arranques de movimiento por segundo**: 1–3 es un buen ritmo.
- **HUECOS**: tramos de más de 0,6 s sin eventos, con la frase en la que caen. Termina con código 1 si hay alguno.

Se puede pasar también un borrador (`salida/borrador.mp4`) para comprobarlo antes del render final.

## Cómo arreglar un hueco

Mira en qué frase cae y qué parte de la frase es (principio, mitad, final). Luego, de más a menos eficaz:

1. **Reparte mejor los momentos** (`en`): si todos caen al principio, pasa el último a una palabra del final.
2. **Cambia a una escena con más momentos**: `lista` (hasta 5), `chat` (5), `barras` (hasta 5), `ficha` (hasta 4),
   `pasos` (hasta 4) aguantan frases largas; `contador`, `objecion`, `tachado` o `imagen` (2) son para frases cortas.
3. **Parte la frase** en dos, cada una con su escena, y vuelve a alinear. Con una voz ya grabada, solo donde la voz
   hace una pausa (si no, el corte cae en mal sitio: alinear.py lo avisa); con ElevenLabs, genera la voz otra vez.
4. **Cambio de pose** del personaje en la palabra del hueco (si hay personaje).
5. **Acorta pausas o acelera** al alinear: `--pausa 0.2` o `--tempo 1.05`.

Al final del vídeo, la escena `cta` hace saltar iconos por turnos para que el cierre no se quede quieto; si
la voz termina mucho antes que el vídeo, baja la cola con `alinear.py … --cola 1.0`.

No pongas efectos de sonido para tapar un hueco: el problema es visual.

## Antes de renderizar

El resumen (`node render.mjs resumen`) ya avisa cuando una escena tarda más de 0,8 s en enseñar algo. Y en la hoja
de contacto, una escena cuyos fotogramas son casi iguales durante varios segundos es un hueco seguro.
