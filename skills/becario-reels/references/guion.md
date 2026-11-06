# Escribir el guion

El guion es lo que más decide si un reel se ve entero. El motor anima lo que le des: si el guion es flojo, el
vídeo será un vídeo bonito que nadie termina.

## Índice
1. Medidas
2. Estructura
3. Ganchos
4. Escribir para la voz
5. Palabras clave (asteriscos)
6. Emociones para ElevenLabs
7. Llamada a la acción
8. Ejemplo completo
9. Cómo enseñárselo al usuario

## 1. Medidas

- **25–60 s** de voz. Menos de 25 s da para poco; más de 60 s pierde a casi todo el mundo. Si el usuario no dice
  nada, apunta a 30–45 s.
- **8–16 frases**, de 6 a 14 palabras (como mucho ~18). Cada frase será una escena: frases largas = escenas largas
  que cuesta mantener vivas.
- A unas 170 palabras por minuto: 45 s ≈ 125 palabras.

## 2. Estructura

1. **Gancho** (1 frase, a veces 2): la razón para quedarse. Va en pantalla como titular.
2. **Promesa o contexto** (1 frase): qué va a ganar quien lo vea («te enseño cómo», «en 30 segundos»).
3. **Desarrollo** (4–10 frases): pasos, ejemplos, datos, comparaciones. Una idea por frase. Ordena de menos a más
   sorprendente para que la curiosidad aguante.
4. **Giro o prueba** (1–2 frases): el dato que lo remata, el resultado, la demostración («y este reel lo ha hecho…»).
5. **Llamada a la acción** (1 frase): comentar, guardar o seguir.

## 3. Ganchos

Concretos, con algo sorprendente o útil y cumplibles. Fórmulas que funcionan (adáptalas al tema, no las copies):

- Dato que choca: «El 80 % de lo que pagas en el súper es marca, no producto.»
- Pregunta con respuesta inesperada: «¿Sabías que tu móvil puede traducir una conversación en directo?»
- Promesa con número: «3 webs gratis que parecen ilegales de lo útiles que son.»
- Antes / después: «Esto me llevaba dos horas. Ahora, dos minutos.»
- Error común: «Si limpias la pantalla con alcohol, la estás rompiendo.»
- Demostración: «Este vídeo lo ha hecho una IA con una sola frase.»

Evita los ganchos que prometen algo que el vídeo no da: la gente se va y no vuelve.

## 4. Escribir para la voz

- Español hablado: frases cortas, sujeto y verbo pronto, nada de paréntesis ni incisos largos.
- Las cifras, en número («3 webs», «el 80 %», «1.500 €»): se leen bien y quedan mejor en pantalla.
- Nombres extranjeros o siglas que la voz pronuncia mal: escribe en `voz` cómo se dicen y deja `texto` bien escrito
  (sale en los subtítulos). Ejemplos para ElevenLabs en español: Claude → «Clod», ChatGPT → «chat yi pi tí»,
  reels → «rils», YouTube → «yutub», iPhone → «aifon». «IA» se lee bien tal cual.
- Signos que ayudan a la entonación: «¿…?» y «¡…!» completos, comas donde se respira, puntos suspensivos para un
  silencio con intención.
- No metas pausas largas a propósito: alinear.py recorta cualquier silencio de más de 0,26 s.

## 5. Palabras clave (asteriscos)

Marca con `*asteriscos*` las 1–2 palabras que importan en cada frase. En los subtítulos salen en una caja del color
de acento, y el resumen avisa si una escena no tiene nada que resaltar.

- Varias palabras seguidas que van juntas: un solo par de asteriscos (`*sin gastar créditos*`) → una sola caja.
- Dos grupos distintos: dos pares (`*rápido* y *gratis*`).
- La puntuación puede ir dentro o fuera (`*entero.*` o `*entero*.`).
- No resaltes más de 3–4 palabras por frase: si todo destaca, nada destaca.

## 6. Emociones para ElevenLabs

Los modelos v4 y v3 de ElevenLabs entienden etiquetas en inglés entre corchetes al principio de la frase. Pon una en
`emocion` en cada frase y cámbiala a lo largo del guion para que la voz no suene plana:

| Etiqueta | Para |
|---|---|
| `[excited]` | gancho, revelaciones, final |
| `[curious]` | preguntas, «¿sabías que…?» |
| `[confident]` | afirmaciones, datos |
| `[playfully]` / `[mischievously]` | ironía, objeciones, «¿pensarás que…?» |
| `[skeptical]` | la duda que vas a desmontar |
| `[impressed]` | el dato que sorprende |
| `[whispers]` | secretos, «esto casi nadie lo sabe» |

Evita risas y suspiros (`[laughs]`, `[sighs]`): alargan las pausas y rompen el ritmo.

`scripts/voz.py` junta las frases con su etiqueta y le da al usuario los pasos para generarla. Las voces de
ElevenLabs suelen ir a 170–200 palabras por minuto; alinear.py dice a cuántas va: si baja de ~190, alinea con
`--tempo 1.05` (5 % más rápida sin cambiar el tono), que en reels se nota para bien.

## 7. Llamada a la acción

- **Comentar una palabra** («Comenta *GUIA* y te la mando»): es la que más interacción da. La palabra debe ser
  corta, en mayúsculas, sin tildes ni eñes (para que la escriban igual y la automatización la reconozca). Solo si el usuario va a mandar algo de verdad (a mano o con una
  automatización, ver publicar.md).
- **Guardar** («Guárdalo para cuando lo necesites»): para listas y trucos.
- **Seguir** («Sígueme para la parte 2»): para series.

Una sola llamada a la acción. Va en la última frase, con la escena `cta`.

## 8. Ejemplo completo

Encargo: «hazme un reel sobre trucos para ahorrar en el súper».

1. `[excited]` *3 trucos* del súper que te ahorran *50 € al mes.* (titular, sin subtítulos)
2. `[confident]` El primero es el más *fácil* y casi nadie lo hace. (pregunta o titular corto)
3. `[curious]` Mira la *estantería de abajo:* ahí están las marcas *más baratas.* (imagen o lista)
4. `[confident]` Las caras se ponen *a la altura de los ojos* a propósito. (comparación)
5. `[playfully]` El segundo: nunca vayas a comprar *con hambre.* (objeción o contador)
6. `[impressed]` Gastas hasta un *15 % más* sin darte cuenta. (contador)
7. `[confident]` Y el tercero: compara el *precio por kilo,* no el del paquete. (comparación)
8. `[surprised]` El paquete grande *no siempre* sale más barato. (tachado)
9. `[excited]` Comenta *LISTA* y te mando *todos los trucos.* (cta)

## 9. Cómo enseñárselo al usuario

Pon el guion numerado en el chat, con las palabras clave en negrita, y en el mismo mensaje pregunta cómo quiere la
voz: generada en ElevenLabs (le das el texto con etiquetas), grabada por él o sin voz. No esperes aprobación frase a
frase: si pide cambios, cámbialo; si no dice nada, sigue.
