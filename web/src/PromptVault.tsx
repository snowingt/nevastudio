import React, { useState } from 'react'

export interface PromptTemplate {
  id: string
  title: string
  category: 'frutinovela' | 'gancho' | 'ventas' | 'documental'
  variables: string[]
  template: string
  description: string
}

const PRELOADED_PROMPTS: PromptTemplate[] = [
  {
    id: 'frutinovela-grid',
    title: 'Frutinovela: Grilla 3x3 y Consistencia Nano Banana',
    category: 'frutinovela',
    variables: ['personaje', 'emocion', 'vestimenta'],
    description: 'Genera 9 tomas con el mismo personaje antropomórfico en diferentes ángulos para Veo 3.1.',
    template: 'A 3x3 photo grid showing 9 consistent shots of an anthropomorphic {{personaje}} wearing {{vestimenta}}, expressing intense {{emocion}}. Photorealistic cinematic lighting, studio lighting, highly detailed texture, 8k vertical framing.'
  },
  {
    id: 'hook-2sec-scroll',
    title: 'Gancho Anti-Scroll de 2 Segundos',
    category: 'gancho',
    variables: ['tema', 'enemigo_comun'],
    description: 'Apertura de alto impacto que frena el pulgar en los primeros 2 segundos.',
    template: 'El 90% de las personas comete este grave error con {{tema}} porque {{enemigo_comun}} les mintió. Quédate hasta el final porque lo que vas a descubrir cambiará todo.'
  },
  {
    id: 'aida-commerce',
    title: 'Guion de Ventas AIDA (B2B & E-Commerce)',
    category: 'ventas',
    variables: ['producto', 'dolor_cliente', 'oferta'],
    description: 'Estructura clásica Atención, Interés, Deseo, Acción orientada a alta conversión.',
    template: '¿Cansado de sufrir con {{dolor_cliente}}? Conoce {{producto}}, la solución definitiva diseñada para multiplicar tus resultados. Aprovecha hoy nuestra oferta exclusiva: {{oferta}}. Toca el botón abajo antes de que se agote.'
  },
  {
    id: 'editor-v1-doc',
    title: 'Estructura Documental Dinámica (Editor V1)',
    category: 'documental',
    variables: ['empresa', 'año', 'hecho_insolito'],
    description: 'Desglose de ritmo rápido con B-roll y pruebas en pantalla cada 1 segundo.',
    template: 'En {{año}}, {{empresa}} estaba al borde del colapso total. Nadie sospechaba que {{hecho_insolito}} no solo los salvaría, sino que los convertiría en un imperio de miles de millones.'
  }
]

interface Props {
  onUsarPrompt?: (prompt: string) => void
}

export function PromptVault({ onUsarPrompt }: Props = {}) {
  const [prompts, setPrompts] = useState<PromptTemplate[]>(PRELOADED_PROMPTS)
  const [activePrompt, setActivePrompt] = useState<PromptTemplate>(PRELOADED_PROMPTS[0])
  const [varValues, setVarValues] = useState<Record<string, string>>({
    personaje: 'Plátano Detective',
    emocion: 'Sorpresa y sospecha',
    vestimenta: 'Gabardina clásica marrón'
  })
  const [copied, setCopied] = useState(false)
  const [search, setSearch] = useState('')
  const [catFilter, setCatFilter] = useState('all')

  const handleSelectPrompt = (p: PromptTemplate) => {
    setActivePrompt(p)
    const defaults: Record<string, string> = {}
    p.variables.forEach(v => { defaults[v] = varValues[v] || '' })
    setVarValues(defaults)
  }

  const getComputedPrompt = () => {
    let res = activePrompt.template
    for (const [k, v] of Object.entries(varValues)) {
      res = res.replaceAll(`{{${k}}}`, v || `[${k}]`)
    }
    return res
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(getComputedPrompt())
    setCopied(true)
    setTimeout(() => setCopied(false), 1800)
  }

  const filtered = prompts.filter(p => {
    const matchCat = catFilter === 'all' || p.category === catFilter
    const matchSearch = !search || p.title.toLowerCase().includes(search.toLowerCase()) || p.description.toLowerCase().includes(search.toLowerCase())
    return matchCat && matchSearch
  })

  return (
    <div className="prompt-vault-view" style={{ padding: '28px 36px', height: '100%', overflowY: 'auto' }}>
      <header style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0, letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: 10 }}>
          <span></span> Banco de Prompts (Prompt Vault)
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 4 }}>
          Plantillas probadas con variables dinámicas para Frutinovelas, Ganchos Virales, Grids 3x3 y Videos de Venta.
        </p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 24 }}>
        {/* Lista Lateral de Plantillas */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <input
            type="text"
            placeholder="Buscar plantilla de prompt..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              padding: '10px 14px',
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid var(--line)',
              borderRadius: 10,
              color: 'var(--text)',
              outline: 'none'
            }}
          />

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: '68vh', overflowY: 'auto' }}>
            {filtered.map(p => (
              <div
                key={p.id}
                className="glass-panel"
                onClick={() => handleSelectPrompt(p)}
                style={{
                  padding: 14,
                  cursor: 'pointer',
                  borderColor: activePrompt.id === p.id ? 'var(--accent)' : 'var(--line)',
                  background: activePrompt.id === p.id ? 'var(--accent-tint)' : 'var(--panel)',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ fontSize: 13.5, fontWeight: 600, color: 'var(--text)', marginBottom: 4 }}>
                  {p.title}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  {p.description}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Editor de Variables Dinámicas y Previsualización */}
        <div className="glass-panel" style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 18 }}>
          <div>
            <span style={{ fontSize: 11, textTransform: 'uppercase', color: 'var(--accent)', fontWeight: 700, letterSpacing: '0.05em' }}>
              {activePrompt.category}
            </span>
            <h2 style={{ fontSize: 19, fontWeight: 600, margin: '4px 0 8px 0' }}>{activePrompt.title}</h2>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: 0 }}>{activePrompt.description}</p>
          </div>

          {/* Formulario de Variables */}
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: 16, borderRadius: 12, border: '1px solid var(--line)' }}>
            <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text)', marginBottom: 12 }}>Variables Dinámicas:</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              {activePrompt.variables.map(v => (
                <div key={v}>
                  <label style={{ display: 'block', fontSize: 11.5, color: 'var(--text-muted)', marginBottom: 4, textTransform: 'capitalize' }}>
                    {v.replace('_', ' ')}
                  </label>
                  <input
                    type="text"
                    value={varValues[v] || ''}
                    placeholder={`Ingresa ${v}...`}
                    onChange={e => setVarValues({ ...varValues, [v]: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      background: 'rgba(255,255,255,0.05)',
                      border: '1px solid var(--line)',
                      borderRadius: 8,
                      color: 'var(--text)',
                      fontSize: 13,
                      outline: 'none'
                    }}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Resultado Computado */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <h3 style={{ fontSize: 13, fontWeight: 600, margin: 0 }}>Prompt Listo para Usar:</h3>
              <div style={{ display: 'flex', gap: 8 }}>
                {onUsarPrompt && (
                  <button
                    type="button"
                    onClick={() => onUsarPrompt(getComputedPrompt())}
                    style={{
                      padding: '6px 14px',
                      borderRadius: 8,
                      background: 'linear-gradient(135deg, #0a84ff, #8b5cf6)',
                      color: '#FFF',
                      fontWeight: 600,
                      fontSize: 12,
                      cursor: 'pointer'
                    }}
                  >
                     Usar en el Estudio
                  </button>
                )}
                <button
                  type="button"
                  onClick={handleCopy}
                  style={{
                    padding: '6px 14px',
                    borderRadius: 8,
                    background: copied ? '#10B981' : 'var(--accent)',
                    color: '#FFF',
                    fontWeight: 600,
                    fontSize: 12,
                    cursor: 'pointer'
                  }}
                >
                  {copied ? '✓ Copiado al Portapapeles' : 'Copiar Prompt'}
                </button>
              </div>
            </div>

            <textarea
              readOnly
              value={getComputedPrompt()}
              style={{
                width: '100%',
                flex: 1,
                minHeight: 180,
                padding: 16,
                background: '#0E0E11',
                border: '1px solid var(--line)',
                borderRadius: 12,
                color: '#E4E4E7',
                fontFamily: 'monospace',
                fontSize: 13,
                lineHeight: 1.6,
                resize: 'none',
                outline: 'none'
              }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
