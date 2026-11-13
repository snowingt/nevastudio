import React, { useEffect, useState } from 'react'

export interface SkillItem {
  id: string
  name: string
  title: string
  description: string
  icon: string
  category: 'video' | 'marketing' | 'drama' | 'edicion' | 'utilidad'
  isCustom?: boolean
}

interface Props {
  onSelectSkill?: (skillId: string) => void
  onClose?: () => void
}

export function SkillsHub({ onSelectSkill, onClose }: Props) {
  const [skills, setSkills] = useState<SkillItem[]>([])
  const [filter, setFilter] = useState<string>('todos')
  const [search, setSearch] = useState<string>('')
  const [showAddModal, setShowAddModal] = useState<boolean>(false)
  const [repoUrl, setRepoUrl] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [statusMsg, setStatusMsg] = useState<string>('')

  useEffect(() => {
    fetch('/api/state')
      .then(r => r.json())
      .then(data => {
        const cards = data.cards || []
        const mapped: SkillItem[] = cards.map((c: any) => ({
          id: c.id,
          name: c.skill || c.id,
          title: c.title,
          description: c.description,
          icon: c.icon || '✦',
          category: c.id.includes('marketer') ? 'marketing' : c.id.includes('drama') ? 'drama' : c.id.includes('documental') ? 'edicion' : 'video'
        }))
        setSkills(mapped)
      })
      .catch(() => {})
  }, [])

  const handleInstallSkill = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!repoUrl) return
    setLoading(true)
    setStatusMsg('Instalando habilidad desde repositorio...')
    try {
      const res = await fetch('/api/skills/install', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: repoUrl })
      })
      const data = await res.json()
      if (res.ok) {
        setStatusMsg('¡Habilidad instalada exitosamente!')
        setTimeout(() => {
          setShowAddModal(false)
          setStatusMsg('')
          setRepoUrl('')
          window.location.reload()
        }, 1200)
      } else {
        setStatusMsg(`Error: ${data.error || 'No se pudo instalar'}`)
      }
    } catch (err: any) {
      setStatusMsg(`Error de red: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const filtered = skills.filter(s => {
    const matchesFilter = filter === 'todos' || s.category === filter
    const matchesSearch = !search || s.title.toLowerCase().includes(search.toLowerCase()) || s.description.toLowerCase().includes(search.toLowerCase())
    return matchesFilter && matchesSearch
  })

  return (
    <div className="skills-hub-view" style={{ padding: '28px 36px', height: '100%', overflowY: 'auto' }}>
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0, letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: 10 }}>
            <span></span> Hub de Habilidades (Skills Hub)
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 4 }}>
            Explora, activa o importa nuevos estilos de video y herramientas comerciales sin tocar código.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowAddModal(true)}
          style={{
            padding: '10px 18px',
            background: 'var(--accent-gradient)',
            color: '#FFF',
            borderRadius: 12,
            fontWeight: 600,
            fontSize: 13,
            boxShadow: '0 4px 14px var(--accent-glow)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 8
          }}
        >
          <span>+</span> Agregar Nueva Habilidad
        </button>
      </header>

      {/* Barra de Filtros y Búsqueda */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 24 }}>
        <input
          type="text"
          placeholder="Buscar habilidad o estilo..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{
            flex: 1,
            padding: '10px 16px',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--line)',
            borderRadius: 12,
            color: 'var(--text)',
            outline: 'none'
          }}
        />

        <div style={{ display: 'flex', gap: 6, background: 'rgba(255,255,255,0.03)', padding: 4, borderRadius: 12, border: '1px solid var(--line)' }}>
          {['todos', 'video', 'edicion', 'marketing', 'drama'].map(cat => (
            <button
              key={cat}
              type="button"
              onClick={() => setFilter(cat)}
              style={{
                padding: '6px 12px',
                borderRadius: 8,
                fontSize: 12,
                textTransform: 'capitalize',
                background: filter === cat ? 'var(--accent)' : 'transparent',
                color: filter === cat ? '#FFF' : 'var(--text-muted)',
                fontWeight: filter === cat ? 600 : 400
              }}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Rejilla de Habilidades Estilo App Store */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 18 }}>
        {filtered.map(s => (
          <div
            key={s.id}
            className="glass-panel"
            style={{
              padding: 20,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              transition: 'transform 0.2s ease, border-color 0.2s ease'
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <div style={{
                  width: 44,
                  height: 44,
                  borderRadius: 12,
                  background: 'rgba(255, 255, 255, 0.08)',
                  display: 'grid',
                  placeItems: 'center',
                  fontSize: 20
                }}>
                  {s.icon === 'video' ? '' : s.icon === 'noticiero' ? '' : s.icon === 'pizarra' ? '' : '✦'}
                </div>
                <span style={{ fontSize: 11, padding: '3px 8px', borderRadius: 999, background: 'rgba(255,255,255,0.06)', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  {s.category}
                </span>
              </div>

              <h3 style={{ fontSize: 16, fontWeight: 600, margin: '0 0 6px 0', color: 'var(--text)' }}>
                {s.title}
              </h3>
              <p style={{ fontSize: 12.5, color: 'var(--text-muted)', lineHeight: 1.5, margin: 0 }}>
                {s.description}
              </p>
            </div>

            <div style={{ marginTop: 20, display: 'flex', gap: 10 }}>
              <button
                type="button"
                onClick={() => onSelectSkill ? onSelectSkill(s.id) : (window.location.hash = `#new:${s.id}`)}
                style={{
                  flex: 1,
                  padding: '9px 14px',
                  background: 'var(--accent-tint)',
                  border: '1px solid var(--accent)',
                  color: 'var(--accent)',
                  borderRadius: 10,
                  fontSize: 12.5,
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                Crear Video con esta Skill
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Modal Agregar Nueva Habilidad */}
      {showAddModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(16px)',
          display: 'grid',
          placeItems: 'center',
          zIndex: 100
        }}>
          <div className="glass-panel" style={{ width: 480, padding: 28 }}>
            <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>+ Importar Nueva Habilidad</h2>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
              Pega una URL de GitHub o repositorio con un `SKILL.md` (ej. una habilidad de replica-skill) para instalarla automáticamente en el estudio.
            </p>

            <form onSubmit={handleInstallSkill}>
              <input
                type="url"
                required
                placeholder="https://github.com/usuario/nombre-skill"
                value={repoUrl}
                onChange={e => setRepoUrl(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px 14px',
                  background: 'rgba(255,255,255,0.06)',
                  border: '1px solid var(--line)',
                  borderRadius: 10,
                  color: '#FFF',
                  marginBottom: 16,
                  outline: 'none'
                }}
              />

              {statusMsg && (
                <div style={{ fontSize: 12.5, color: statusMsg.startsWith('Error') ? '#EF4444' : '#10B981', marginBottom: 14 }}>
                  {statusMsg}
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  style={{ padding: '8px 16px', borderRadius: 8, color: 'var(--text-muted)' }}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    padding: '8px 18px',
                    borderRadius: 8,
                    background: 'var(--accent)',
                    color: '#FFF',
                    fontWeight: 600,
                    cursor: loading ? 'wait' : 'pointer'
                  }}
                >
                  {loading ? 'Instalando...' : 'Instalar Habilidad'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
