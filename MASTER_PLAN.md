# MASTER PLAN & KANBAN: ESTUDIO DE CREACIÓN Y MARKETING IA (CLEAN-ROOM REPLICA)

## REGLAS DE EJECUCIÓN PARA EL AGENTE (ANTIGRAVITY)
1. **Ejecución Secuencial Estricta:** Prohibido intentar programar todos los Sprints en una sola respuesta. Ejecuta **UN SOLO SPRINT a la vez**.
2. **Verificación entre Sprints:** Al terminar cada tarea de un Sprint, ejecuta `npm run typecheck` (o verifica que el servidor y la UI compilen sin errores), marca la casilla como `[x]` en este archivo `MASTER_PLAN.md` y pasa inmediatamente al siguiente punto.
3. **Regla Clean-Room (`replica-skill`):** Cero rastros visuales, nombres, dominios o colores de la app original (cero marcas heredadas). Todo el código nuevo o refactorizado debe llevar la nueva identidad y estética Apple Studio.

---

## 📋 TABLERO KANBAN DE EJECUCIÓN (8 SPRINTS)

### SPRINT 1: Reconocimiento, Auditoría de Skills y Limpieza de Marca (`/replica-recon` & `/replica-brand`)
- [x] **1.1. Clonado y Estructura Base:** Clonar repositorio base como punto de partida y crear la carpeta `replica/` para el registro de cambios.
- [x] **1.2. Auditoría y Renombrado Comercial de las Skills Existentes:**
  - Inspeccionar la carpeta `skills/` y `cards.json` originales.
  - **NO usar los nombres originales** (eliminar nombres como "El Diff" o referencias internas). Renombrarlos a nombres descriptivos y comerciales en la UI y en `cards.json`:
    - *Skill de Edición / Documental (basada en Editor V1)* ➡️ **"Estudio de Edición Dinámica & Documental"** (Conservar y potenciar toda su capacidad de corte en línea de tiempo, B-roll, zooms y edición multicapa).
    - *Skill "El Diff"* ➡️ **"Noticiero Vertical & Resumen de Impacto"**.
    - *Skill "Explicativo 3D"* ➡️ **"Recorrido Visual 3D Sin Cortes"**.
    - *Skill "Reel de Comedia"* ➡️ **"Formato Sketch & Diálogo Rápido"**.
- [x] **1.3. Barrido de Marca (`sweep.py`) y Licencias Gumroad:**
  - Eliminar la carpeta `licencias/` (Cloudflare Worker complejo) y `nube/`.
  - Crear `server/services/gumroad-license.ts` (15 líneas) que valide `license_key` contra `https://api.gumroad.com/v2/licenses/verify`, detecte el tier comprado (`Creator`, `Marketer`, `Agency`) y lo guarde cifrado con `safeStorage` de Electron.

---

### SPRINT 2: Instalador "Zero-Dependency" (Desde Cero) y Evaluador de Hardware (`/replica-architect`)
- [x] **2.1. Bootstrapper Automático para PCs Limpias (`electron/bootstrap.ts`):**
  - Si la app se instala en una PC recién formateada sin Node, Python o FFmpeg, la app NO debe fallar ni pedir terminal.
  - Al iniciar por primera vez, verificar e instalar/descargar silenciosamente en la carpeta interna de datos de la app (`app.getPath('userData')/runtimes/`):
    - Binarios estáticos de **FFmpeg / FFprobe** (`ffmpeg-static`).
    - Entorno **Python Standalone Embebido** (`python-build-standalone` / `uv` portable) sin tocar el sistema operativo del usuario.
    - Navegador Chromium/Chrome gestionado o detección del Chrome local para CDP.
  - Mostrar una pantalla de bienvenida estilo macOS Setup Assistant con barra de progreso limpia mientras descarga los motores la primera vez.
- [x] **2.2. Analizador de Hardware y Estimador de Tiempos (`server/services/hardware-profiler.ts`):**
  - Al arrancar, leer con `os` y `systeminformation`: modelo de CPU, núcleos, cantidad de RAM total/libre y presencia de GPU dedicada (NVIDIA/AMD) vs Integrada.
  - Clasificar el equipo en 3 niveles visibles en la UI:
    - **Gama Baja (<8GB RAM):** Recomendar solo estilos 2D/Canvas y voces rápidas en nube (Edge-TTS/Gemini).
    - **Gama Media (12GB–16GB RAM sin GPU NVIDIA, ej. i7 + gráfica integrada):** Habilitar **Clonación de Voz Local** avisando en pantalla: *"Tu equipo es Gama Media: clonar 1 minuto de voz tomará ~2 minutos. Videos con diseño procedural tomarán ~3-4 min; videos 3D pesados tomarán ~25-40 min"*.
    - **Gama Alta (16GB+ RAM con GPU dedicada):** Todo habilitado en modo turbo.
  - Mostrar en cada *Card* de estilo de video una etiqueta con el **tiempo estimado de renderizado** calculado según el hardware real de esa PC.

---

### SPRINT 3: Motor de Clonación de Voz Local + TTS Ultrarrápido (`python/procesos/`)
- [x] **3.1. Integración del Clonador de Voz Local (Optimizado para 12GB RAM):**
  - Empaquetar en el entorno Python local el motor de clonación de voz ligera por CPU/GPU (optimizado con ONNX / cuantización para que en máquinas de 12GB RAM clone 1 minuto de audio en ~2 minutos sin desbordar la memoria).
  - Crear interfaz en la app para subir un audio de referencia de 15–30 segundos, bautizar la voz clonada y guardarla en la biblioteca local de voces.
  - Añadir aviso automático de requisitos: recomendar mínimo equipo Gama Media (12GB RAM) cuando el usuario active el clonador local, liberando procesos en segundo plano antes de clonar.
- [x] **3.2. Motor TTS Rápido sin GPU (Por defecto para Lotes):**
  - Integrar **Edge-TTS** y **Gemini TTS** que devuelven tanto el archivo `.mp3` como el mapa exacto de subtítulos palabra por palabra (`timestamps.json` / `.vtt`) en 3 segundos, evitando correr Whisper pesado cuando el usuario usa voces generadas.

---

### SPRINT 4: Rediseño Visual Apple Studio + Switch Creator / Marketer (`/replica-design`)
- [x] **4.1. Sistema de Diseño "Cupertino Dark Glass" (`web/src/styles/`):**
  - Fondo `#09090B`, paneles translúcidos `rgba(24, 24, 27, 0.72)` con `backdrop-filter: blur(24px)`, bordes finos `1px solid rgba(255, 255, 255, 0.08)`, tipografía `SF Pro Display / Inter`, radios de `16px`.
- [x] **4.2. Switch Maestro Superior (Dynamic Island Toggle):**
  - Píldora interactiva en el header que cambia toda la experiencia de la app entre dos modos:
    - **🎬 Modo Creator (Acento Violeta `#8B5CF6`):** Enfocado en canales faceless, Frutinovelas, Micro-dramas, Rayos X Neuro-Mecánico y monetización viral.
    - **📈 Modo Marketer (Acento Azul/Esmeralda `#0EA5E9`):** Enfocado en empresas, videos de producto, anuncios AIDA, testimonios y manejo multi-cliente.
- [x] **4.3. Simplificación UX a Wizard de 3 Pasos:**
  - Ocultar complejidades técnicas y presentar el estudio como 3 pasos guiados: **1. Idea y Guion** ➡️ **2. Voz y Escenas (con editor visual)** ➡️ **3. Render y Publicación**.

---

### SPRINT 5: Pestaña de Habilidades (Skills Hub), Biblioteca Multimedia y Banco de Prompts (`/replica-build`)
- [x] **5.1. Empaquetado de Nuevas Skills Nativas en `skills/`:**
  - Integrar junto a las skills auditadas del Sprint 1:
    1. `skill-xray-motion`: Estética Rayos X Neuro-Mecánico (`1080x1920`, grafito y amarillo neón con esquemas Zod).
    2. `skill-procedural-canvas`: Motor continuo de 3 etapas (*Paper → Blueprint → Hologram* a 120 BPM sin cortes).
    3. `skill-frutinovelas-microdrama`: Generador de micro-novelas, historias de personajes antropomórficos (frutinovelas) y K-dramas de 60s con consistencia de personaje.
    4. `skill-marketer-commerce`: Plantillas para empresas, servicios locales y catálogos con llamados a la acción.
- [x] **5.2. Nueva Pestaña "🧩 Habilidades (Skills Hub)" Extensible:**
  - Crear vista en la interfaz donde el usuario ve todas las habilidades instaladas como tarjetas estilo App Store.
  - Botón **"+ Agregar Nueva Habilidad"** que permita al usuario importar una carpeta, un archivo `.zip`, un `SKILL.md` o pegar una URL de GitHub para instalar nuevos estilos de video o capacidades de edición sin tocar código.
- [x] **5.3. Nueva Pestaña "🖼️ Biblioteca Multimedia (Media Gallery)":**
  - Galería visual estilo *Apple Photos / Final Cut* con filtros rápidos: **[Todos]**, **[Videos Renderizados]**, **[Imágenes Generadas]**, **[Voces y Audios]**.
  - Permite previsualizar en grande, ver metadatos (fecha, prompt usado, duración), reutilizar cualquier imagen o audio en un nuevo proyecto con un clic, o abrir su carpeta en el sistema.
- [x] **5.4. Nueva Pestaña "📚 Banco de Prompts (Prompt Vault)":**
  - Base de datos local con buscador, etiquetas y variables dinámicas (`{{personaje}}`, `{{tema}}`, `{{tono}}`) pre-cargada con plantillas para Frutinovelas, Ganchos Virales, Grids 3x3 de personajes y Guiones de Ventas.

---

### SPRINT 6: Panel Lateral "Pi Agent Copilot" con Control Total de la App
- [x] **6.1. Integración de Pi Agent Multi-Provider:**
  - Panel de chat colapsable a la derecha de la ventana.
  - Selector de cerebro en un clic: **Antigravity (Local Bridge/MCP)**, **Claude**, **Codex / OpenAI**, **Gemini Flash** (API Key gratuita) u **OpenCode**.
- [x] **6.2. Skill Maestra `app-omniscient-controller`:**
  - Dotar a Pi Agent de herramientas internas (`tools`) para operar la app por el usuario no técnico: crear proyectos, redactar guiones de frutinovelas o campañas de empresa, editar escenas usando la *Skill de Edición*, guardar en el Banco de Prompts y enviar videos a la cola de lotes.
  - Incluir botones de acción rápida ("Chips") y botón **"Aplicar cambios al video"** dentro de las respuestas del chat.

---

### SPRINT 7: Bóveda de Navegador Persistente (CDP) + Fábrica en Lotes (`/replica-backend`)
- [x] **7.1. "Ghost Browser Vault" con Ciberseguridad (`electron/browser-vault.ts`):**
  - Lanzar instancia dedicada de Chrome/Chromium con puerto dinámico aleatorio (`--remote-debugging-port=0`) y perfil aislado por cuenta/cliente.
  - Cifrar cookies y tokens de sesión en disco usando `safeStorage` nativo de Electron (AES-256 atado al SO) + `--password-store=basic` en Linux para que jamás pida volver a iniciar sesión al cerrar el navegador.
  - **Regla estricta CDP:** Usar siempre `browser.disconnect()` al terminar una automatización; prohibido usar `browser.close()`.
- [x] **7.2. Autopublicación Sin APIs y Modo Fábrica por Lotes (`server/batch-factory.ts`):**
  - Automatizar vía CDP la subida y programación de videos terminados en **YouTube Studio, TikTok Studio e Instagram/Meta Business Suite**.
  - Crear cola de procesamiento en segundo plano donde el usuario carga de 5 a 20 ideas y la app genera guiones, voces, renders y publicaciones de forma desatendida.

---

### SPRINT 8: Pruebas, Verificación de Paridad y Empaquetado Comercial (`/replica-test` & `/replica-deploy`)
- [x] **8.1. Verificación y Limpieza Final:**
  - Ejecutar `sweep.py` para confirmar 0 referencias a la marca anterior.
  - Comprobar que todas las vistas (Estudio, Biblioteca, Banco de Prompts, Habilidades, Lotes, Cuentas y Pi Agent) funcionen sin errores.
- [x] **8.2. Compilador de Instaladores (`electron-builder`):**
  - Configurar generación de instaladores de un clic para Windows (`.exe`), macOS (`.dmg`) y Linux (`.AppImage`).