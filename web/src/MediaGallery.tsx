import React, { useEffect, useState } from 'react'

export interface MediaItem {
  id: string
  name: string
  type: 'video' | 'image' | 'audio'
  url: string
  path: string
  sizeBytes: number
  durationSeconds?: number
  createdAt: string
  prompt?: string
}

export function MediaGallery() {
  const [items, setItems] = useState<MediaItem[]>([])
  const [filter, setFilter] = useState<'all' | 'video' | 'image' | 'audio'>('all')
  const [search, setSearch] = useState('')
  const [selectedItem, setSelectedItem] = useState<MediaItem | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/media/list')
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data)) setItems(data)
      })
      .catch(() => {})
  }, [])

  const copyPath = (item: MediaItem) => {
    navigator.clipboard.writeText(item.path)
    setCopiedId(item.id)
    setTimeout(() => setCopiedId(null), 1800)
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const filtered = items.filter(it => {
    const matchesFilter = filter === 'all' || it.type === filter
    const matchesSearch = !search || it.name.toLowerCase().includes(search.toLowerCase()) || (it.prompt || '').toLowerCase().includes(search.toLowerCase())
    return matchesFilter && matchesSearch
  })

  return (
    <div className="media-gallery-view" style={{ padding: '28px 36px', height: '100%', overflowY: 'auto' }}>
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0, letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: 10 }}>
            <span></span> Biblioteca Multimedia (Media Gallery)
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 4 }}>
            Visualiza, reproduce y reutiliza tus videos renderizados, imágenes generadas y voces clonadas.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 6, background: 'rgba(255,255,255,0.03)', padding: 4, borderRadius: 12, border: '1px solid var(--line)' }}>
          {[
            { id: 'all', label: 'Todos' },
            { id: 'video', label: 'Videos Renderizados' },
            { id: 'image', label: 'Imágenes Generadas' },
            { id: 'audio', label: 'Voces y Audios' }
          ].map(f => (
            <button
              key={f.id}
              type="button"
              onClick={() => setFilter(f.id as any)}
              style={{
                padding: '6px 14px',
                borderRadius: 8,
                fontSize: 12.5,
                background: filter === f.id ? 'var(--accent)' : 'transparent',
                color: filter === f.id ? '#FFF' : 'var(--text-muted)',
                fontWeight: filter === f.id ? 600 : 400
              }}
            >
              {f.label}
            </button>
          ))}
        </div>
      </header>

      {/* Rejilla Visual Estilo Apple Photos */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 16 }}>
        {filtered.map(item => (
          <div
            key={item.id}
            className="glass-panel"
            onClick={() => setSelectedItem(item)}
            style={{
              overflow: 'hidden',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              transition: 'transform 0.2s ease, box-shadow 0.2s ease'
            }}
          >
            <div style={{ height: 160, background: '#121214', display: 'grid', placeItems: 'center', position: 'relative' }}>
              {item.type === 'image' && (
                <img src={item.url} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              )}
              {item.type === 'video' && (
                <video src={item.url} style={{ width: '100%', height: '100%', objectFit: 'cover' }} muted />
              )}
              {item.type === 'audio' && (
                <div style={{ fontSize: 36, color: 'var(--accent)' }}></div>
              )}

              <span style={{
                position: 'absolute',
                bottom: 8,
                right: 8,
                padding: '2px 8px',
                background: 'rgba(0,0,0,0.7)',
                backdropFilter: 'blur(8px)',
                borderRadius: 6,
                fontSize: 11,
                color: '#FFF'
              }}>
                {item.type.toUpperCase()}
              </span>
            </div>

            <div style={{ padding: '12px 14px' }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {item.name}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11.5, color: 'var(--text-muted)', marginTop: 4 }}>
                <span>{formatSize(item.sizeBytes)}</span>
                <span>{new Date(item.createdAt).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        ))}

        {filtered.length === 0 && (
          <div style={{ gridColumn: '1 / -1', padding: 48, textAlign: 'center', color: 'var(--text-muted)' }}>
            No hay elementos multimedia en esta categoría.
          </div>
        )}
      </div>

      {/* Modal de Previsualización en Detalle */}
      {selectedItem && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.8)',
            backdropFilter: 'blur(20px)',
            display: 'grid',
            placeItems: 'center',
            zIndex: 100
          }}
          onClick={() => setSelectedItem(null)}
        >
          <div
            className="glass-panel"
            style={{ width: 620, padding: 24, maxHeight: '90vh', overflowY: 'auto' }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h2 style={{ fontSize: 17, fontWeight: 600, margin: 0 }}>{selectedItem.name}</h2>
              <button type="button" onClick={() => setSelectedItem(null)} style={{ fontSize: 18, color: 'var(--text-muted)' }}>✕</button>
            </div>

            <div style={{ borderRadius: 12, overflow: 'hidden', background: '#000', marginBottom: 16, display: 'grid', placeItems: 'center', maxHeight: 360 }}>
              {selectedItem.type === 'video' && <video src={selectedItem.url} controls autoPlay style={{ maxWidth: '100%', maxHeight: 360 }} />}
              {selectedItem.type === 'image' && <img src={selectedItem.url} alt={selectedItem.name} style={{ maxWidth: '100%', maxHeight: 360, objectFit: 'contain' }} />}
              {selectedItem.type === 'audio' && <audio src={selectedItem.url} controls autoPlay style={{ width: '85%', margin: '20px 0' }} />}
            </div>

            <div style={{ background: 'rgba(255,255,255,0.03)', padding: 14, borderRadius: 10, fontSize: 12.5, lineHeight: 1.6, marginBottom: 16 }}>
              <div><strong>Ruta del archivo:</strong> <code style={{ wordBreak: 'break-all' }}>{selectedItem.path}</code></div>
              <div><strong>Tamaño:</strong> {formatSize(selectedItem.sizeBytes)}</div>
              <div><strong>Creado:</strong> {new Date(selectedItem.createdAt).toLocaleString()}</div>
              {selectedItem.prompt && <div><strong>Prompt utilizado:</strong> {selectedItem.prompt}</div>}
            </div>

            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
              <button
                type="button"
                onClick={() => copyPath(selectedItem)}
                style={{ padding: '8px 14px', borderRadius: 8, background: 'rgba(255,255,255,0.08)', color: 'var(--text)', fontSize: 12.5 }}
              >
                {copiedId === selectedItem.id ? '✓ Ruta Copiada' : 'Copiar Ruta'}
              </button>
              <button
                type="button"
                onClick={() => {
                  window.location.hash = `#new:video-documental`
                  setSelectedItem(null)
                }}
                style={{ padding: '8px 16px', borderRadius: 8, background: 'var(--accent)', color: '#FFF', fontWeight: 600, fontSize: 12.5 }}
              >
                Reutilizar en Nuevo Proyecto
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
