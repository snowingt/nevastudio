import React, { useState } from 'react'

export type PiBrain = 'antigravity' | 'claude' | 'codex' | 'gemini' | 'opencode'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  actions?: Array<{
    type: string
    label: string
    payload: any
  }>
}

interface Props {
  activeSessionId?: string
  activeCardId?: string
  onApplyEdits?: (payload: any) => void
}

export function PiAgentPanel({ activeSessionId, activeCardId, onApplyEdits }: Props) {
  const [isOpen, setIsOpen] = useState(false)
  const [brain, setBrain] = useState<PiBrain>('antigravity')
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: '¡Hola! Soy **Pi Agent**, tu copiloto de producción. ¿Quieres crear una Frutinovela, un guion comercial B2B o ajustar la edición de tu video?'
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [appliedMsgId, setAppliedMsgId] = useState<string | null>(null)

  const chips = [
    'Crear Frutinovela 3x3',
    'Gancho Viral de 2s',
    'Campaña B2B con AIDA',
    'Aplicar B-roll y zooms'
  ]

  const sendMessage = async (textToSend?: string) => {
    const text = textToSend || input
    if (!text.trim() || loading) return

    const userMsg: Message = { id: `usr_${Date.now()}`, role: 'user', content: text }
    const updated = [...messages, userMsg]
    setMessages(updated)
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('/api/pi-agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: brain,
          messages: updated,
          activeSessionId,
          activeCardId
        })
      })
      const data = await res.json()
      if (data?.message) {
        setMessages([...updated, data.message])
      }
    } catch {
      setMessages([...updated, {
        id: `err_${Date.now()}`,
        role: 'assistant',
        content: 'Hubo un error de conexión con el cerebro seleccionado.'
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleAction = (act: any, msgId: string) => {
    if (act.type === 'apply_edits') {
      onApplyEdits?.(act.payload)
      setAppliedMsgId(msgId)
      setTimeout(() => setAppliedMsgId(null), 2500)
    }
  }

  return (
    <>
      {/* Botón flotante para abrir Pi Agent */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          height: 48,
          padding: '0 18px',
          background: 'var(--accent-gradient)',
          color: '#FFF',
          borderRadius: 999,
          boxShadow: '0 10px 28px var(--accent-glow)',
          display: 'flex',
          alignItems: 'center',
          gap: 9,
          fontWeight: 600,
          fontSize: 13.5,
          zIndex: 80,
          cursor: 'pointer',
          border: '1px solid rgba(255,255,255,0.15)'
        }}
      >
        <span>✦</span> Pi Copilot
      </button>

      {/* Panel Lateral Deslizante Estilo Cupertino Dark Glass */}
      {isOpen && (
        <aside
          className="glass-panel"
          style={{
            position: 'fixed',
            top: 14,
            right: 14,
            bottom: 14,
            width: 390,
            zIndex: 90,
            display: 'flex',
            flexDirection: 'column',
            boxShadow: '-16px 0 48px rgba(0,0,0,0.65)',
            border: '1px solid var(--line)',
            overflow: 'hidden'
          }}
        >
          {/* Header con Selector de Cerebro */}
          <div style={{ padding: '16px 18px', borderBottom: '1px solid var(--line)', display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 700, fontSize: 15 }}>
                <span style={{ fontSize: 17 }}>✦</span> Pi Agent Copilot
              </div>
              <button type="button" onClick={() => setIsOpen(false)} style={{ color: 'var(--text-muted)', fontSize: 18, cursor: 'pointer' }}>
                ✕
              </button>
            </div>

            {/* Selector de Cerebro en un Clic */}
            <div style={{ display: 'flex', gap: 4, background: 'rgba(255,255,255,0.04)', padding: 3, borderRadius: 10 }}>
              {(['antigravity', 'claude', 'codex', 'gemini', 'opencode'] as PiBrain[]).map(b => (
                <button
                  key={b}
                  type="button"
                  onClick={() => setBrain(b)}
                  style={{
                    flex: 1,
                    padding: '5px 2px',
                    borderRadius: 8,
                    fontSize: 10.5,
                    textTransform: 'capitalize',
                    background: brain === b ? 'var(--accent)' : 'transparent',
                    color: brain === b ? '#FFF' : 'var(--text-muted)',
                    fontWeight: brain === b ? 600 : 400
                  }}
                >
                  {b === 'antigravity' ? 'AGY' : b}
                </button>
              ))}
            </div>
          </div>

          {/* Mensajes */}
          <div style={{ flex: 1, overflowY: 'auto', padding: 18, display: 'flex', flexDirection: 'column', gap: 14 }}>
            {messages.map(m => (
              <div
                key={m.id}
                style={{
                  alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '88%',
                  background: m.role === 'user' ? 'var(--accent)' : 'rgba(255, 255, 255, 0.05)',
                  color: '#FFF',
                  padding: '12px 14px',
                  borderRadius: 14,
                  fontSize: 13,
                  lineHeight: 1.5,
                  border: m.role === 'user' ? 'none' : '1px solid var(--line)'
                }}
              >
                <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>

                {/* Acciones interactivas (ej: Aplicar cambios al video) */}
                {m.actions && (
                  <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {m.actions.map(act => (
                      <button
                        key={act.label}
                        type="button"
                        onClick={() => handleAction(act, m.id)}
                        style={{
                          padding: '7px 12px',
                          background: appliedMsgId === m.id ? '#10B981' : 'rgba(255,255,255,0.12)',
                          border: '1px solid rgba(255,255,255,0.2)',
                          color: '#FFF',
                          borderRadius: 8,
                          fontSize: 12,
                          fontWeight: 600,
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 6
                        }}
                      >
                        {appliedMsgId === m.id ? '✓ Cambios Aplicados al Video' : act.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div style={{ alignSelf: 'flex-start', color: 'var(--text-muted)', fontSize: 12 }}>
                Pi Agent pensando con {brain}...
              </div>
            )}
          </div>

          {/* Chips Sugeridos */}
          <div style={{ padding: '8px 16px', display: 'flex', gap: 6, overflowX: 'auto', borderTop: '1px solid var(--line)' }}>
            {chips.map(c => (
              <button
                key={c}
                type="button"
                onClick={() => sendMessage(c)}
                style={{
                  whiteSpace: 'nowrap',
                  padding: '4px 10px',
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid var(--line)',
                  borderRadius: 999,
                  fontSize: 11,
                  color: 'var(--text-muted)',
                  cursor: 'pointer'
                }}
              >
                {c}
              </button>
            ))}
          </div>

          {/* Input de Envío */}
          <div style={{ padding: 14, borderTop: '1px solid var(--line)', display: 'flex', gap: 8 }}>
            <input
              type="text"
              placeholder="Pide un guion, B-roll o ajuste..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
              style={{
                flex: 1,
                padding: '10px 14px',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--line)',
                borderRadius: 10,
                color: '#FFF',
                fontSize: 13,
                outline: 'none'
              }}
            />
            <button
              type="button"
              onClick={() => sendMessage()}
              disabled={!input.trim()}
              style={{
                padding: '0 16px',
                background: 'var(--accent)',
                color: '#FFF',
                borderRadius: 10,
                fontWeight: 600,
                cursor: input.trim() ? 'pointer' : 'default',
                opacity: input.trim() ? 1 : 0.4
              }}
            >
              ➤
            </button>
          </div>
        </aside>
      )}
    </>
  )
}
