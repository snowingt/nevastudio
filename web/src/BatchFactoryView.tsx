import React, { useState, useEffect } from 'react'
import './cupertino-glass.css'

interface BatchItem {
  id: string
  idea: string
  style: string
  voice: string
  platforms: string[]
  status: 'pending' | 'scripting' | 'voice' | 'rendering' | 'publishing' | 'done' | 'failed'
  progress: number
  videoPath?: string
  error?: string
}

export function BatchFactoryView() {
  const [queue, setQueue] = useState<BatchItem[]>([])
  const [loading, setLoading] = useState(false)
  const [ideasInput, setIdeasInput] = useState('')
  const [selectedStyle, setSelectedStyle] = useState('video-documental')
  const [selectedVoice, setSelectedVoice] = useState('es-MX-DaliaNeural')
  const [ytUpload, setYtUpload] = useState(true)
  const [ttUpload, setTtUpload] = useState(true)
  const [igUpload, setIgUpload] = useState(false)

  const loadQueue = async () => {
    try {
      const res = await fetch('/api/batch/queue')
      if (res.ok) {
        const data = await res.json()
        setQueue(data.queue || [])
      }
    } catch {
      // Fallback local
    }
  }

  useEffect(() => {
    loadQueue()
    const timer = setInterval(loadQueue, 4000)
    return () => clearInterval(timer)
  }, [])

  const handleEnqueue = async () => {
    const rawIdeas = ideasInput.split('\n').map(s => s.trim()).filter(Boolean)
    if (rawIdeas.length === 0) return

    setLoading(true)
    const platforms: string[] = []
    if (ytUpload) platforms.push('youtube')
    if (ttUpload) platforms.push('tiktok')
    if (igUpload) platforms.push('meta')

    try {
      const res = await fetch('/api/batch/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ideas: rawIdeas,
          style: selectedStyle,
          voice: selectedVoice,
          platforms
        })
      })
      if (res.ok) {
        setIdeasInput('')
        await loadQueue()
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="glass-panel" style={{ margin: '24px auto', maxWidth: 960, padding: 32 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 24, fontWeight: 700, letterSpacing: '-0.5px' }}>
             Fábrica de Contenido por Lotes (Batch Engine)
          </h2>
          <p style={{ margin: '6px 0 0 0', color: '#A1A1AA', fontSize: 14 }}>
            Generación y autopublicación desatendida vía CDP para 5 a 20 ideas simultáneas.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <span className="glass-chip active" style={{ fontSize: 13, background: 'rgba(16, 185, 129, 0.15)', color: '#10B981', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
            ● Motor Desatendido Activo
          </span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: 24, marginBottom: 32 }}>
        {/* Input de Ideas */}
        <div style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid var(--glass-border)', borderRadius: 16, padding: 20 }}>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#E4E4E7', marginBottom: 8 }}>
            Ingresa de 5 a 20 ideas (una por línea):
          </label>
          <textarea
            value={ideasInput}
            onChange={(e) => setIdeasInput(e.target.value)}
            placeholder={`5 secretos psicológicos que usan los millonarios\nPor qué el café de especialidad nunca sabe amargo\nLa regla de los 2 minutos explicada en 30 segundos\nEl error financiero más común a los 25 años\nCómo hackear tu enfoque matutino sin dopamina`}
            rows={7}
            style={{
              width: '100%',
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 12,
              color: '#F4F4F5',
              padding: 12,
              fontSize: 13,
              fontFamily: 'inherit',
              resize: 'vertical'
            }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 12 }}>
            <span style={{ fontSize: 12, color: '#71717A' }}>
              {ideasInput.split('\n').filter(s => s.trim()).length} ideas detectadas
            </span>
            <button
              onClick={handleEnqueue}
              disabled={loading || !ideasInput.trim()}
              className="glass-button glass-button-primary"
              style={{ padding: '8px 20px', fontSize: 14 }}
            >
              {loading ? 'Encolando...' : ' Lanzar Lote Desatendido'}
            </button>
          </div>
        </div>

        {/* Configuración del Lote */}
        <div style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid var(--glass-border)', borderRadius: 16, padding: 20 }}>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#E4E4E7', marginBottom: 12 }}>
            Configuración de Producción
          </label>

          <div style={{ marginBottom: 14 }}>
            <span style={{ fontSize: 12, color: '#A1A1AA', display: 'block', marginBottom: 4 }}>Estilo Cinematográfico:</span>
            <select
              value={selectedStyle}
              onChange={(e) => setSelectedStyle(e.target.value)}
              style={{
                width: '100%',
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 8,
                color: '#fff',
                padding: '6px 10px',
                fontSize: 13
              }}
            >
              <option value="video-documental">Edición Dinámica & Documental</option>
              <option value="video-el-diff">Noticiero Vertical & Resumen</option>
              <option value="video-explicativo">Recorrido Visual 3D Sin Cortes</option>
              <option value="skill-xray-motion">Radiografía Kinetic & Anatomía</option>
              <option value="skill-procedural-canvas">Procedural Generativo 60s</option>
              <option value="skill-frutinovelas-microdrama">Frutinovela Micro-Drama</option>
              <option value="skill-marketer-commerce">Comercial B2B & Producto</option>
            </select>
          </div>

          <div style={{ marginBottom: 14 }}>
            <span style={{ fontSize: 12, color: '#A1A1AA', display: 'block', marginBottom: 4 }}>Voz de Locución:</span>
            <select
              value={selectedVoice}
              onChange={(e) => setSelectedVoice(e.target.value)}
              style={{
                width: '100%',
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 8,
                color: '#fff',
                padding: '6px 10px',
                fontSize: 13
              }}
            >
              <option value="es-MX-DaliaNeural">Dalia (Español México - Dinámica)</option>
              <option value="es-MX-JorgeNeural">Jorge (Español México - Profesional)</option>
              <option value="es-ES-AlvaroNeural">Álvaro (Español España - Enérgico)</option>
              <option value="es-CO-GonzaloNeural">Gonzalo (Español Colombia - Cálido)</option>
            </select>
          </div>

          <div>
            <span style={{ fontSize: 12, color: '#A1A1AA', display: 'block', marginBottom: 6 }}>Canales de Autopublicación (CDP):</span>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 13 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                <input type="checkbox" checked={ytUpload} onChange={(e) => setYtUpload(e.target.checked)} />
                <span>YouTube Studio (Shorts)</span>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                <input type="checkbox" checked={ttUpload} onChange={(e) => setTtUpload(e.target.checked)} />
                <span>TikTok Studio</span>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                <input type="checkbox" checked={igUpload} onChange={(e) => setIgUpload(e.target.checked)} />
                <span>Meta Business Suite (Reels)</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Cola de Render y Autopublicación */}
      <div>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: '#E4E4E7', marginBottom: 14 }}>
          Cola Activa de Procesamiento ({queue.length} elementos)
        </h3>

        {queue.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 20px', border: '1px dashed var(--glass-border)', borderRadius: 16, color: '#71717A' }}>
            No hay videos en la cola en este momento. Ingresa tus ideas arriba para arrancar la fábrica.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {queue.map((item, idx) => (
              <div
                key={item.id || idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '14px 18px',
                  background: 'rgba(255,255,255,0.02)',
                  border: '1px solid rgba(255,255,255,0.06)',
                  borderRadius: 12
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 14, flex: 1, minWidth: 0 }}>
                  <span style={{ fontSize: 12, fontWeight: 700, color: '#71717A', width: 24 }}>#{idx + 1}</span>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 14, fontWeight: 500, color: '#F4F4F5', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {item.idea}
                    </div>
                    <div style={{ fontSize: 12, color: '#71717A', marginTop: 2 }}>
                      Estilo: {item.style} · Canales: {item.platforms?.join(', ') || 'Solo render'}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  <span
                    style={{
                      fontSize: 12,
                      fontWeight: 600,
                      padding: '4px 10px',
                      borderRadius: 100,
                      background:
                        item.status === 'done' ? 'rgba(16, 185, 129, 0.2)' :
                        item.status === 'failed' ? 'rgba(239, 68, 68, 0.2)' :
                        'rgba(14, 165, 233, 0.2)',
                      color:
                        item.status === 'done' ? '#10B981' :
                        item.status === 'failed' ? '#EF4444' :
                        '#0EA5E9'
                    }}
                  >
                    {item.status === 'pending' && 'En espera'}
                    {item.status === 'scripting' && 'Redactando guión...'}
                    {item.status === 'voice' && 'Sintetizando voz...'}
                    {item.status === 'rendering' && `Renderizando (${item.progress || 0}%)`}
                    {item.status === 'publishing' && 'Publicando CDP...'}
                    {item.status === 'done' && 'Completado'}
                    {item.status === 'failed' && 'Error'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
