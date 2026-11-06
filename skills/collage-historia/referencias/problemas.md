# Si algo falla

| Síntoma | Qué hacer |
| --- | --- |
| `Permission denied` o `Read-only file system` al escribir | Trabajas en la carpeta de la skill. Cópiala con el comando de SKILL.md (con `chmod -R u+w`) y trabaja en la copia. |
| `No encuentro …/palabras.json` | Falta alinear la voz: `alinear.py … --salida P/voz` (o `--sin-voz`). |
| «video.json tiene N frases y la voz tiene M» | Tiene que haber un objeto en `frases` por cada línea de `guion.txt`. Una línea vacía no cuenta; una línea con dos frases, sí es una sola. |
| «Palabras reconocidas» por debajo del 80 % | `guion.txt` no es lo que dice la voz. Corrige el texto (o quita las etiquetas que se leyeron en voz alta) y repite. |
| No baja el modelo de voz (403 o sin red) | `alinear.py` prueba Hugging Face y, si no, npm (comprueba el sha256). Sin red: `--sin-voz` para probar, o pasa `--modelo CARPETA` con un faster-whisper ya descargado. |
| `pip` no puede instalar (sin permisos de administrador) | `python3 -m pip install --user faster-whisper` (y `--break-system-packages` si lo pide). |
| «no encuentro la palabra … para colocar un elemento» | Esa palabra no está en esa frase del guion. Usa otra, o segundos (`"en": 1.2`). |
| Un elemento tapa el titular o los subtítulos | Mantén los elementos entre y = 450 y 1280; baja el `ancho`. |
| El render se corta (límite de tiempo del entorno) | Repite el mismo comando: el cuerpo va por tandas de 20 s y sigue donde iba. Para ver el ritmo antes, `--rapido`. |
| El segundo final vuelve a montar todo | El cuerpo solo se reutiliza si nada ha cambiado antes de la última frase (plan y voz). Es normal la primera vez tras un cambio. |
| `ritmo.py` avisa de tramos quietos | En ese segundo, añade un elemento con `en`, una línea de titular con `@` o un cambio de pose. |
| La cita se oye cortada o con otra frase | Ajusta `tramos` escuchando el clip (`trozos.py transcribir` da la pista, no la verdad). |
| La carpeta `salida/` ocupa mucho | `salida/partes/` es la caché del cuerpo por tandas (sirve para el segundo final). Cuando tengas los vídeos definitivos, se puede borrar. Las hojas (`*_hoja.png`), transcripciones y `fotograma_*.png` también son de trabajo. |
