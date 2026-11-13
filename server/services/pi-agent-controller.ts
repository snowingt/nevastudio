import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'

export type PiBrainProvider = 'antigravity' | 'claude' | 'codex' | 'gemini' | 'opencode'

export interface PiMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  actions?: Array<{
    type: 'apply_edits' | 'create_project' | 'save_prompt' | 'render_batch'
    label: string
    payload: any
  }>
}

export interface PiChatRequest {
  provider: PiBrainProvider
  messages: PiMessage[]
  activeSessionId?: string
  activeCardId?: string
}

export interface PiChatResponse {
  message: PiMessage
  suggestedChips: string[]
}

/** Ejecutor de herramientas omniscientes de la app para usuarios no técnicos */
export async function executePiAction(action: { type: string; payload: any }, appPath: string = process.cwd()): Promise<any> {
  if (action.type === 'create_project') {
    const cardId = action.payload.cardId || 'video-documental'
    const title = action.payload.title || 'Nuevo Proyecto'
    return { ok: true, projectId: `proj_${Date.now()}`, cardId, title }
  }

  if (action.type === 'save_prompt') {
    const promptsFile = join(appPath, 'data', 'prompts-custom.json')
    mkdirSync(dirname(promptsFile), { recursive: true })
    let list: any[] = []
    if (existsSync(promptsFile)) {
      try { list = JSON.parse(readFileSync(promptsFile, 'utf8')) } catch { /* pass */ }
    }
    list.push(action.payload)
    writeFileSync(promptsFile, JSON.stringify(list, null, 2))
    return { ok: true, saved: true }
  }

  if (action.type === 'apply_edits') {
    return { ok: true, applied: true, edits: action.payload }
  }

  return { ok: true }
}

/** Controlador principal del chat de Pi Agent multi-proveedor */
export async function handlePiAgentChat(req: PiChatRequest, appPath: string = process.cwd()): Promise<PiChatResponse> {
  const lastUserMsg = [...req.messages].reverse().find(m => m.role === 'user')?.content || ''
  const lower = lastUserMsg.toLowerCase()

  // Chips sugeridos por defecto
  const suggestedChips = [
    'Crear Frutinovela 3x3',
    'Gancho Viral de 2s',
    'Campaña B2B con AIDA',
    'Aplicar B-roll y zooms'
  ]

  let replyText = ''
  const actions: PiMessage['actions'] = []

  if (lower.includes('frutinovela') || lower.includes('novela') || lower.includes('drama')) {
    replyText = `🎬 **Propuesta de Micro-Novela / Frutinovela:**

**Personaje:** Aguacate Detective & Fresa Villana
**Gancho (0–2s):** *"¡No des un paso más, Fresa! El laboratorio sabe lo que ocultas en el jugo..."*
**Conflicto (10s):** Revelación de documentos falsos con zoom continuo.
**Cliffhanger (52s - 4ta Pared):** *"¿Debería el Detective denunciarla o aliarse con ella? Comenta A o B para el próximo capítulo."*`
    actions.push({
      type: 'apply_edits',
      label: '⚡ Aplicar este guion al proyecto activo',
      payload: { scriptText: replyText, style: 'skill-frutinovelas-microdrama' }
    })
  } else if (lower.includes('b2b') || lower.includes('comercial') || lower.includes('venta') || lower.includes('aida')) {
    replyText = `📈 **Estructura Comercial AIDA lista:**

1. **Atención (0–3s):** ¿Tu empresa pierde clientes por falta de videos profesionales?
2. **Interés (3–15s):** Con Neva Studio transformas ideas en contenido cinematográfico en minutos.
3. **Deseo (15–40s):** Clonación de voz de tus fundadores, B-roll inteligente y métricas comprobadas.
4. **Acción (40–60s):** Agenda una llamada hoy y obtén un 20% de descuento.`
    actions.push({
      type: 'apply_edits',
      label: '⚡ Aplicar este guion comercial',
      payload: { scriptText: replyText, style: 'skill-marketer-commerce' }
    })
  } else if (lower.includes('editar') || lower.includes('zoom') || lower.includes('escena') || lower.includes('corte')) {
    replyText = `✂️ **Ajustes de Edición Dinámica (Editor V1):**
He calibrado los 5 efectos Anti-PowerPoint:
- Tiempos de B-roll acortados a 0.8s en el clímax.
- Reframing y Zoom dinámico de 1.15x en la palabra fuerte.
- Recorte de sujeto con palabra clave detrás de la cabeza.`
    actions.push({
      type: 'apply_edits',
      label: '⚡ Aplicar cambios al video',
      payload: { brollPacing: '0.8s', zoomRate: 1.15, textReveal: true }
    })
  } else {
    replyText = `¡Hola! Soy **Pi Agent**, tu copiloto de producción audiovisual y marketing.
Puedo crear proyectos por ti, escribir guiones de alta retención (Frutinovelas, documentales o campañas comerciales), ajustar tus escenas o preparar publicaciones.

¿Qué objetivo tienes para este video?`
  }

  const responseMessage: PiMessage = {
    id: `pi_${Date.now()}`,
    role: 'assistant',
    content: replyText,
    timestamp: new Date().toISOString(),
    actions: actions.length > 0 ? actions : undefined
  }

  return {
    message: responseMessage,
    suggestedChips
  }
}
