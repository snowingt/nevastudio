# Elegir la historia y escribir el guion

## Qué historia funciona
Una buena historia-metáfora cumple las cuatro:
1. **Se reconoce en un segundo**: una película o serie muy vista, una fábula, un mito o un hecho histórico conocido.
2. **Tiene una frase o un momento clave** que resume la idea («cuando todos sean súper, nadie lo será»).
3. **El paralelismo con el tema es claro** sin explicarlo mucho: quien mira piensa «¿te suena?» antes de que lo digas.
4. **El usuario tiene clips** de ese momento (o, en una fábula o un hecho real, imágenes propias o de dominio público).

Cuando propongas tres historias, que sean de tipos distintos:
| Tipo | Ejemplo de paralelismo |
| --- | --- |
| Cine o serie | Un villano que reparte poderes a todos → herramientas que hacen que todo el mundo produzca lo mismo |
| Fábula o mito | La liebre y la tortuga → aprender un poco cada día gana a los atracones |
| Hecho real | Un invento que se vendió como el fin de un oficio → lo que pasó de verdad con ese oficio |

Para cada una, una línea: la historia, el momento clave y el paralelismo. Que el usuario elija.

## Estructura del guion (12–18 frases; en corto, 8–11)
| Bloque | Frases | Qué hace |
| --- | --- | --- |
| Gancho | 1 | Un dato concreto o una afirmación rara: «Un villano de X predijo hace más de 20 años lo que pasa hoy con Y». |
| La historia | 6–8 | Quién era, qué quería, qué le pasó y **la frase clave**. Frases cortas, en presente o pasado sencillo. |
| El giro | 1–2 | «¿Te suena?» y el paralelismo con el tema, con ejemplos concretos. |
| Desarrollo | 2–3 | Por qué importa, con datos comprobados. |
| El matiz | 1–2 | La objeción («¿entonces no hay que…? No.») y en qué se equivocaba el personaje. |
| La idea | 1–2 | Lo que se lleva quien mira, dicho de forma que se recuerde. |
| Final | 1 | Llamada a la acción («Comenta PALABRA…» o «Sígueme…»). |

- Una idea por frase. Cada frase tiene algo que se pueda **ver** (un objeto, un gesto, un número): eso será su elemento en el collage.
- Unas 195 palabras por minuto: 60 s son unas 195 palabras.
- Marca con `**…**` las 1–3 palabras clave de cada frase (salen en la caja de color de los subtítulos).
- **La primera línea de `guion.txt` es la primera frase que se oye.** Nada de títulos ni de notas en el archivo: una frase por línea.

## Datos y citas
- Fechas, nombres y cifras: búscalos en una fuente fiable y apunta la fuente y el día de la consulta para la descripción. Si no puedes comprobar algo, quítalo o dilo como opinión.
- **Si las fuentes no coinciden** (fechas antiguas, cifras redondeadas), usa la forma más prudente que sea verdad en todas («hace más de 2.500 años», «más de 20 años») y no des un año exacto.
- **Citas de la historia:** usa la frase exacta del clip que tiene el usuario (`trozos.py transcribir` y escúchala). Los doblajes cambian las frases: la de un país puede no coincidir con la de otro.
- Si la cita no se oye bien, dilo y usa una paráfrasis («viene a decir que…»).

## Texto para ElevenLabs (u otra voz sintética)
- El mismo guion, con una etiqueta de emoción al principio de algunas frases: `[excited]`, `[curious]`, `[confident]`, `[skeptical]`, `[mischievously]`, `[playfully]`, `[impressed]`.
- Sin `**` y con los nombres extranjeros escritos como suenan («Clod» por Claude, «skil» por skill). Los subtítulos salen de `guion.txt`, que sí va bien escrito.
- Si hay dos finales: el texto completo con el primero, y aparte solo la frase del segundo.
- Después de grabar, `alinear.py` mide las palabras por minuto. Si sale por debajo de 185, `--velocidad 1.05`.
