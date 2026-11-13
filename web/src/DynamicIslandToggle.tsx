import React, { useEffect, useState } from 'react'

export type StudioMode = 'creator' | 'marketer'

interface Props {
  onModeChange?: (mode: StudioMode) => void
}

export function DynamicIslandToggle({ onModeChange }: Props) {
  const [mode, setMode] = useState<StudioMode>(() => {
    try {
      const saved = localStorage.getItem('nevastudio_mode')
      return (saved === 'marketer' || saved === 'creator') ? saved : 'creator'
    } catch {
      return 'creator'
    }
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-mode', mode)
    try {
      localStorage.setItem('nevastudio_mode', mode)
    } catch { /* storage fallback */ }
    onModeChange?.(mode)
  }, [mode, onModeChange])

  return (
    <div className="dynamic-island-container">
      <div className="dynamic-island-pill" role="tablist" aria-label="Selector de Modo de Estudio">
        <button
          type="button"
          className={`dynamic-island-btn ${mode === 'creator' ? 'active' : ''}`}
          onClick={() => setMode('creator')}
          role="tab"
          aria-selected={mode === 'creator'}
          title="Modo Creator: Enfoque en micro-novelas, faceless, YouTube Shorts, TikTok y monetización viral"
        >
          <span className="dynamic-island-icon"></span>
          <span>Modo Creator</span>
          {mode === 'creator' && <span className="dynamic-island-badge">Viral</span>}
        </button>

        <button
          type="button"
          className={`dynamic-island-btn ${mode === 'marketer' ? 'active' : ''}`}
          onClick={() => setMode('marketer')}
          role="tab"
          aria-selected={mode === 'marketer'}
          title="Modo Marketer: Enfoque en anuncios para empresas, catálogo, videos de producto y ventas AIDA"
        >
          <span className="dynamic-island-icon"></span>
          <span>Modo Marketer</span>
          {mode === 'marketer' && <span className="dynamic-island-badge">B2B</span>}
        </button>
      </div>
    </div>
  )
}
