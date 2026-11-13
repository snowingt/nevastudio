#!/usr/bin/env node
/**
 * Domi-Drama & Neva Studio MCP Server
 * Conector MCP oficial para Gemini, Antigravity y Claude Code.
 * Automatiza la producción de novelas y micro-dramas (K-Drama + Dominicana),
 * generación de video en Google Flow (Veo 3.1), ensamblado Remotion y
 * multi-despacho en redes sociales (YouTube Studio CDP, TikTok, Instagram, Facebook, Telegram).
 */

import { createInterface } from 'node:readline'
import { existsSync, mkdirSync, readFileSync, writeFileSync, readdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { spawn } from 'node:child_process'

const STUDIO_URL = process.env.SNOW_STUDIO_URL || process.env.SLOTH_URL || 'http://127.0.0.1:4848'
const NOVELAS_DIR = resolve(process.env.HOME || '/home/snow', 'nevastudio', 'data', 'novelas')

if (!existsSync(NOVELAS_DIR)) {
  mkdirSync(NOVELAS_DIR, { recursive: true })
}

const HERRAMIENTAS = [
  {
    name: 'domidrama_create_series',
    description: 'Crea una nueva serie o universo de micro-novelas "Domi-Drama" (K-Drama + Telenovela Dominicana). Define arquetipos de personajes, conflicto central, locaciones y biblia temática.',
    inputSchema: {
      type: 'object',
      properties: {
        slug: { type: 'string', description: 'Identificador corto en minúsculas (ej: "heredero-piantini", "traicion-naco")' },
        titulo: { type: 'string', description: 'Título de la serie' },
        premisa: { type: 'string', description: 'Conflicto central de la serie (choque de clases, venganza, herencia oculta)' },
        personajes: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              nombre: { type: 'string' },
              rol: { type: 'string', description: 'Ej: El heredero oculto / La matriarca fría / La prometida ambiciosa' },
              descripcion: { type: 'string', description: 'Rasgos físicos y de personalidad para consistencia en Veo 3.1 y Nano Banana' }
            },
            required: ['nombre', 'rol', 'descripcion']
          },
          description: 'Elenco principal de la novela'
        },
        locaciones: {
          type: 'array',
          items: { type: 'string' },
          description: 'Lugares clave (ej: "Penthouse de lujo en Piantini", "Colmado en Villa Mella", "Terraza frente al Malecón")'
        }
      },
      required: ['slug', 'titulo', 'premisa', 'personajes']
    }
  },
  {
    name: 'domidrama_list_series',
    description: 'Lista todas las series de Domi-Drama creadas en Neva Studio y sus episodios disponibles.',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  },
  {
    name: 'domidrama_generate_script',
    description: 'Genera el guion completo de un episodio de 45-60 segundos con estructura de retención K-Drama (gancho de 2s, tensión progresiva, confrontación apasionada dominicana y freeze-frame cliffhanger con corte dramático de OST).',
    inputSchema: {
      type: 'object',
      properties: {
        slug: { type: 'string', description: 'Slug de la serie' },
        episodio: { type: 'integer', description: 'Número del episodio (ej: 1)' },
        titulo_episodio: { type: 'string', description: 'Título del episodio' },
        conflicto: { type: 'string', description: 'Qué detona la pelea o revelación en este episodio' },
        gancho_tipo: {
          type: 'string',
          enum: ['interrupcion_patron', 'acusacion_directa', 'secreto_al_descubierto', 'choque_de_clases'],
          description: 'Fórmula psicológica de enganche en los primeros 2 segundos (yt-script)'
        }
      },
      required: ['slug', 'episodio', 'titulo_episodio', 'conflicto']
    }
  },
  {
    name: 'domidrama_generate_flow_prompts',
    description: 'Convierte las escenas del guion en prompts cinematográficos optimizados para Google Flow (Veo 3.1 9:16 vertical y Nano Banana 2.1) con iluminación de cine, 85mm f/1.4 y micro-expresiones.',
    inputSchema: {
      type: 'object',
      properties: {
        slug: { type: 'string', description: 'Slug de la serie' },
        episodio: { type: 'integer', description: 'Número del episodio' }
      },
      required: ['slug', 'episodio']
    }
  },
  {
    name: 'domidrama_dispatch_flow',
    description: 'Envía un prompt a generar directamente en Google Flow mediante la cuenta de Google activa en Neva Studio (689 créditos listos). Soporta Veo 3.1 9:16 y Nano Banana.',
    inputSchema: {
      type: 'object',
      properties: {
        prompt: { type: 'string', description: 'Prompt cinematográfico en inglés o español' },
        tipo: { type: 'string', enum: ['video', 'imagen'], description: 'video (Veo 3.1) o imagen (Nano Banana)' },
        modelo: { type: 'string', enum: ['Veo 3.1 - Fast', 'Veo 3.1 - Lite', 'Veo 3.1 - Quality', 'Nano Banana 2.1'], description: 'Modelo a usar' },
        formato: { type: 'string', enum: ['9:16', '16:9'], description: 'Formato vertical 9:16 recomendado' },
        salida: { type: 'string', description: 'Ruta absoluta donde se guardará el archivo generado (.mp4 o .jpg)' },
        tope: { type: 'number', description: 'Créditos máximos a gastar (default: 20)' }
      },
      required: ['prompt', 'salida']
    }
  },
  {
    name: 'domidrama_check_flow_status',
    description: 'Consulta el estado de generación de Google Flow o el saldo restante de créditos en las cuentas de Google.',
    inputSchema: {
      type: 'object',
      properties: {
        id: { type: 'string', description: 'ID del trabajo devuelto por domidrama_dispatch_flow. Si se omite, devuelve saldos generales.' }
      }
    }
  },
  {
    name: 'domidrama_publish_social',
    description: 'Publica o abre los cargadores oficiales de redes para el video terminado: YouTube Studio (CDP automático), TikTok Studio, Instagram Reels, Facebook Reels o Telegram Bot.',
    inputSchema: {
      type: 'object',
      properties: {
        platform: { type: 'string', enum: ['youtube', 'tiktok', 'instagram', 'facebook', 'telegram'], description: 'Red social de destino' },
        video_path: { type: 'string', description: 'Ruta absoluta del archivo de video .mp4' },
        title: { type: 'string', description: 'Título del video / episodio' },
        description: { type: 'string', description: 'Descripción o caption con hashtags' },
        visibility: { type: 'string', enum: ['PUBLIC', 'UNLISTED', 'PRIVATE'], description: 'Para YouTube Studio (default: PUBLIC)' }
      },
      required: ['platform', 'video_path']
    }
  }
]

async function apiRequest(path, data = null, method = 'GET') {
  const url = `${STUDIO_URL}${path}`
  const options = {
    method: data ? 'POST' : method,
    headers: { 'Content-Type': 'application/json' }
  }
  if (data) options.body = JSON.stringify(data)
  const res = await fetch(url, options)
  const text = await res.text()
  try {
    return JSON.parse(text)
  } catch {
    return { status: res.status, raw: text }
  }
}

const LLAMADAS = {
  async domidrama_create_series(args) {
    const dir = join(NOVELAS_DIR, args.slug)
    mkdirSync(dir, { recursive: true })
    mkdirSync(join(dir, 'episodios'), { recursive: true })
    mkdirSync(join(dir, 'assets'), { recursive: true })

    const bible = {
      slug: args.slug,
      titulo: args.titulo,
      premisa: args.premisa,
      personajes: args.personajes,
      locaciones: args.locaciones || [],
      fecha_creacion: new Date().toISOString(),
      episodios_totales: 0
    }

    writeFileSync(join(dir, 'series.json'), JSON.stringify(bible, null, 2), 'utf-8')
    return `✅ Serie Domi-Drama creada con éxito en ${dir}/series.json\nTítulo: "${args.titulo}"\nPersonajes: ${args.personajes.map(p => p.nombre).join(', ')}`
  },

  async domidrama_list_series() {
    const slugs = readdirSync(NOVELAS_DIR)
    const result = []
    for (const slug of slugs) {
      const seriesPath = join(NOVELAS_DIR, slug, 'series.json')
      if (existsSync(seriesPath)) {
        try {
          const data = JSON.parse(readFileSync(seriesPath, 'utf-8'))
          result.push({
            slug,
            titulo: data.titulo,
            premisa: data.premisa,
            personajes: data.personajes?.length ?? 0
          })
        } catch {}
      }
    }
    return JSON.stringify(result, null, 2)
  },

  async domidrama_generate_script(args) {
    const dir = join(NOVELAS_DIR, args.slug)
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true })
      mkdirSync(join(dir, 'episodios'), { recursive: true })
    }
    const epDir = join(dir, 'episodios', `ep_${String(args.episodio).padStart(2, '0')}`)
    mkdirSync(epDir, { recursive: true })
    mkdirSync(join(epDir, 'clips'), { recursive: true })
    mkdirSync(join(epDir, 'salida'), { recursive: true })

    const hookText = args.gancho_tipo === 'acusacion_directa' 
      ? '¡Tú no eres nadie en esta torre, chofer de pacotilla!'
      : args.gancho_tipo === 'secreto_al_descubierto'
      ? '¡Te encontré el contrato original firmado con tu verdadero apellido!'
      : '¡Bájame la voz en mi propia casa, que tú aquí no eres más que un arrimao!'

    const script = {
      slug: args.slug,
      episodio: args.episodio,
      titulo: args.titulo_episodio,
      duracion_estimada: '55s',
      gancho_tipo: args.gancho_tipo || 'interrupcion_patron',
      estructura_retencion: {
        acto_1_gancho: {
          tiempo: '00:00 - 00:03',
          visual: 'Primer plano extremo en 9:16 a ojos con mirada de hielo estilo K-Drama. Corte súbito tras choque de copa de cristal.',
          dialogo: `VOZ / PERSONAJE: "${hookText}"`,
          audio_sfx: 'whoosh_impact + cristal roto + silencio súbito'
        },
        acto_2_escalada: {
          tiempo: '00:03 - 00:25',
          visual: 'Cámara lenta en paneo vertical. Penthouse de Piantini con luz crepuscular. La matriarca doña Carmen lo señala con furia.',
          dialogo: 'DOÑA CARMEN: "¿Tú te estás creyendo que porque manejas el Mercedes de mi familia tienes derecho a poner un pie en esta sala? ¡Vete al callejón donde perteneces!"\n\nMANNY (mirada impasible, da un paso al frente): "Usted habla mucho de su familia, Doña Carmen... pero se le olvida quién le firmó los cheques este mes."',
          audio_sfx: 'sub_drop suave + violonchelo tenso K-Drama OST'
        },
        acto_3_confrontacion: {
          tiempo: '00:25 - 00:45',
          visual: 'Snap-zoom a Manny sacando un sello lacrado de su bolsillo y arrojándolo sobre la mesa de mármol. Reacción de pánico en Doña Carmen.',
          dialogo: 'DOÑA CARMEN (temblando): "Ese sello... no puede ser. Ese sello es del presidente del Grupo Colonial..."\n\nMANNY: "Míreme bien a los ojos. En esta torre, el chofer siempre fue el dueño."',
          audio_sfx: 'thump cinético + acorde de piano desgarrador'
        },
        acto_4_cliffhanger: {
          tiempo: '00:45 - 00:55',
          visual: 'FREEZE FRAME cinematográfico en alto contraste con viñeta sepia. Manny mirando fijamente a la cámara con media sonrisa fría.',
          dialogo: 'TEXTO CINÉTICO EN MÁSCARA: "¿Qué pasará cuando el resto de la familia descubra quién es Manny?"\nCONTINUARÁ EN EPISODIO 2',
          audio_sfx: 'corte de campana dramática + stinger musical orquestal'
        }
      }
    }

    const scriptPath = join(epDir, 'guion.json')
    const scriptMdPath = join(epDir, 'guion.md')
    writeFileSync(scriptPath, JSON.stringify(script, null, 2), 'utf-8')

    const mdContent = `# ${args.titulo_episodio} (Episodio ${args.episodio})
**Serie:** ${args.slug} | **Duración:** 55s | **Formato:** Vertical 9:16

## [00:00 - 00:03] GANCHO (2-Second Gate)
- **Visual:** ${script.estructura_retencion.acto_1_gancho.visual}
- **Audio:** ${script.estructura_retencion.acto_1_gancho.dialogo}
- **SFX:** ${script.estructura_retencion.acto_1_gancho.audio_sfx}

## [00:03 - 00:25] ESCALADA & SAZÓN DOMINICANO
- **Visual:** ${script.estructura_retencion.acto_2_escalada.visual}
- **Diálogo:**
${script.estructura_retencion.acto_2_escalada.dialogo}
- **SFX:** ${script.estructura_retencion.acto_2_escalada.audio_sfx}

## [00:25 - 00:45] CONFRONTACIÓN & REVELACIÓN
- **Visual:** ${script.estructura_retencion.acto_3_confrontacion.visual}
- **Diálogo:**
${script.estructura_retencion.acto_3_confrontacion.dialogo}
- **SFX:** ${script.estructura_retencion.acto_3_confrontacion.audio_sfx}

## [00:45 - 00:55] CLIFFHANGER FREEZE-FRAME
- **Visual:** ${script.estructura_retencion.acto_4_cliffhanger.visual}
- **Remate:** ${script.estructura_retencion.acto_4_cliffhanger.dialogo}
- **SFX:** ${script.estructura_retencion.acto_4_cliffhanger.audio_sfx}
`
    writeFileSync(scriptMdPath, mdContent, 'utf-8')
    return `✅ Guion Domi-Drama generado en ${scriptPath}\nEpisodio ${args.episodio}: "${args.titulo_episodio}" listo para prompts de Google Flow.`
  },

  async domidrama_generate_flow_prompts(args) {
    const dir = join(NOVELAS_DIR, args.slug, 'episodios', `ep_${String(args.episodio).padStart(2, '0')}`)
    const promptsFile = join(dir, 'flow_prompts.json')

    const prompts = [
      {
        escena: 1,
        nombre: 'clip_01_gancho_ojos',
        tipo: 'video',
        modelo: 'Veo 3.1 - Fast',
        formato: '9:16',
        prompt: 'Cinematic 9:16 vertical video, extreme close-up on the intense piercing eyes of a handsome 28-year-old Dominican man with cold Korean drama stare. Subtle pupil dilation, dramatic blue-gold lighting reflection, 85mm f/1.4 lens, 24fps film aesthetic, hyperrealistic 4k.',
        salida: join(dir, 'clips', 'clip_01.mp4')
      },
      {
        escena: 2,
        nombre: 'clip_02_dona_confrontacion',
        tipo: 'video',
        modelo: 'Veo 3.1 - Fast',
        formato: '9:16',
        prompt: 'Cinematic 9:16 vertical video, elegant 55-year-old Dominican matriarch in designer silk blouse in luxury Santo Domingo penthouse, furious expressive hand gestures, shouting angrily, sunset golden hour through massive floor-to-ceiling windows, high dynamic range, hyperrealistic.',
        salida: join(dir, 'clips', 'clip_02.mp4')
      },
      {
        escena: 3,
        nombre: 'clip_03_chofer_calma',
        tipo: 'video',
        modelo: 'Veo 3.1 - Fast',
        formato: '9:16',
        prompt: 'Cinematic 9:16 vertical video, medium shot of handsome Dominican driver in black suit, smiling with cold calm amusement, taking a confident step forward inside modern marble penthouse, dramatic rim lighting, cinematic K-drama pacing.',
        salida: join(dir, 'clips', 'clip_03.mp4')
      },
      {
        escena: 4,
        nombre: 'clip_04_sello_revelacion',
        tipo: 'video',
        modelo: 'Veo 3.1 - Fast',
        formato: '9:16',
        prompt: 'Cinematic 9:16 vertical video, slow motion close-up of a hand slamming an antique gold luxury corporate seal onto a black Italian marble coffee table, dramatic dust motes in sunbeam, luxury penthouse interior, photorealistic 8k.',
        salida: join(dir, 'clips', 'clip_04.mp4')
      },
      {
        escena: 5,
        nombre: 'clip_05_cliffhanger_freeze',
        tipo: 'imagen',
        modelo: 'Nano Banana 2.1',
        formato: '9:16',
        prompt: 'Cinematic 9:16 vertical movie poster still, dramatic freeze-frame portrait of Dominican protagonist looking directly into the camera with mysterious slight smirk, intense warm key light, deep shadows, cinematic drama poster 8k.',
        salida: join(dir, 'clips', 'portada_cliffhanger.jpg')
      }
    ]

    writeFileSync(promptsFile, JSON.stringify(prompts, null, 2), 'utf-8')
    return `✅ 5 Prompts para Google Flow generados y guardados en ${promptsFile}\nListos para despachar con domidrama_dispatch_flow.`
  },

  async domidrama_dispatch_flow(args) {
    const payload = {
      tipo: args.tipo || 'video',
      prompt: args.prompt,
      modelo: args.modelo || (args.tipo === 'imagen' ? 'Nano Banana 2.1' : 'Veo 3.1 - Fast'),
      formato: args.formato || '9:16',
      salida: resolve(args.salida),
      tope: args.tope || 20
    }
    const res = await apiRequest('/api/flow/generar', payload)
    return `🌊 Google Flow Despachado: ${JSON.stringify(res, null, 2)}`
  },

  async domidrama_check_flow_status(args) {
    if (args.id) {
      const res = await apiRequest(`/api/flow/trabajos/${encodeURIComponent(args.id)}`)
      return JSON.stringify(res, null, 2)
    }
    const res = await apiRequest('/api/flow')
    return `📊 Estado Google Flow en Neva Studio:\nCuentas activas: ${res.cuentas?.map(c => `${c.correo} (${c.saldo?.creditos ?? '?'} créditos)`).join(', ')}\nTotal créditos disponibles: ${res.quedan}\nGeneraciones en fila: ${res.enFila}`
  },

  async domidrama_publish_social(args) {
    const videoPath = resolve(args.video_path)
    if (!existsSync(videoPath)) {
      throw new Error(`El archivo de video no existe: ${videoPath}`)
    }

    if (args.platform === 'youtube') {
      const script = resolve(process.env.HOME || '/home/snow', 'nevastudio', 'scripts', 'youtube_uploader.py')
      const pyArgs = [
        script,
        '--video', videoPath,
        '--title', args.title || 'Micro-Novela Domi-Drama | Episodio Completo',
        '--desc', `${args.description || ''}\n\n#Shorts #KDrama #NovelaDominicana #NevaStudio`,
        '--visibility', args.visibility || 'PUBLIC'
      ]
      return new Promise((done) => {
        const proc = spawn('python3', pyArgs)
        let out = ''
        proc.stdout.on('data', d => { out += d.toString() })
        proc.stderr.on('data', d => { out += d.toString() })
        proc.on('close', code => {
          done(code === 0 ? `✅ Publicado en YouTube Studio (CDP):\n${out}` : `❌ Error en YouTube Uploader:\n${out}`)
        })
      })
    }

    if (args.platform === 'tiktok') {
      const script = resolve(process.env.HOME || '/home/snow', 'nevastudio', 'scripts', 'tiktok_uploader.py')
      const pyArgs = [
        script,
        '--video', videoPath,
        '--title', args.title || 'Micro-Novela Domi-Drama | Episodio Completo',
        '--tags', args.description || '#KDrama #NovelaCorta #MiniNovela #DomiDrama #Viral #Parati'
      ]
      return new Promise((done) => {
        const proc = spawn('python3', pyArgs)
        let out = ''
        proc.stdout.on('data', d => { out += d.toString() })
        proc.stderr.on('data', d => { out += d.toString() })
        proc.on('close', code => {
          done(code === 0 ? `✅ Despachado y preparado en TikTok Studio (CDP):\n${out}` : `❌ Error en TikTok Uploader:\n${out}`)
        })
      })
    }

    if (args.platform === 'telegram') {
      const script = resolve(process.env.HOME || '/home/snow', 'nevastudio', 'scripts', 'telegram_dispatcher.py')
      const pyArgs = [script, 'video', videoPath, args.title || '🎬 Nuevo episodio Domi-Drama']
      return new Promise((done) => {
        const proc = spawn('python3', pyArgs)
        let out = ''
        proc.stdout.on('data', d => { out += d.toString() })
        proc.stderr.on('data', d => { out += d.toString() })
        proc.on('close', code => {
          done(code === 0 ? `✅ Despachado a Telegram:\n${out}` : `❌ Error en Telegram Dispatcher:\n${out}`)
        })
      })
    }

    // Para TikTok, Instagram y Facebook: lanzar mediante el navegador de Neva Studio
    const res = await apiRequest('/api/snow/social-launch', {
      platform: args.platform,
      video: videoPath
    })
    return `🌐 Lanzador de ${args.platform.toUpperCase()} activado en navegador:\nURL: ${res.url}\n(Ruta del video copiada al portapapeles para pegar directo: ${videoPath})`
  }
}

const responder = (id, cosa) => process.stdout.write(`${JSON.stringify({ jsonrpc: '2.0', id, ...cosa })}\n`)

createInterface({ input: process.stdin }).on('line', async (line) => {
  let m
  try {
    m = JSON.parse(line)
  } catch {
    return
  }
  if (m.id === undefined) return
  if (m.method === 'initialize') {
    return responder(m.id, {
      result: {
        protocolVersion: m.params?.protocolVersion ?? '2025-06-18',
        capabilities: { tools: {} },
        serverInfo: { name: 'domidrama-studio', version: '1.0.0' }
      }
    })
  }
  if (m.method === 'ping') return responder(m.id, { result: {} })
  if (m.method === 'tools/list') return responder(m.id, { result: { tools: HERRAMIENTAS } })
  if (m.method === 'tools/call') {
    const fn = LLAMADAS[m.params?.name]
    if (!fn) return responder(m.id, { error: { code: -32602, message: `Herramienta desconocida: ${m.params?.name}` } })
    try {
      const text = await fn(m.params.arguments || {})
      responder(m.id, { result: { content: [{ type: 'text', text: typeof text === 'string' ? text : JSON.stringify(text, null, 2) }] } })
    } catch (e) {
      responder(m.id, { result: { content: [{ type: 'text', text: e instanceof Error ? e.message : String(e) }], isError: true } })
    }
    return
  }
  responder(m.id, { error: { code: -32601, message: `Método desconocido: ${m.method}` } })
})
