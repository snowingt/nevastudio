import { useEffect, useState } from 'react'
import type { Card, SessionMeta, VideoFinal } from '../../shared/types'
import { api } from './api'
import { YoutubeBoton } from './Youtube'
import './Final.css'

/**
 * Lo que se hace con un video terminado, arriba de la fase Entrega del estudio: bajarlo, verlo en su carpeta y pedirle
 * un cambio de un clic. Los cambios le llegan al agente como si los escribieras, y no se pueden pedir mientras trabaja.
 */

/** Lo que pide cada cambio de un clic. `conVoz`: vale también cuando la voz es una grabación del usuario (El Diff). */
const CAMBIOS: { texto: string; pide: string; conVoz?: boolean }[] = [
  { texto: 'Hazlo más corto', pide: 'Hazlo más corto: quita lo que sobra y deja lo esencial, sin perder el gancho ni el cierre.' },
  { texto: 'Dale más ritmo', pide: 'Dale más ritmo: cortes más rápidos, menos pausas y más movimiento, con la música y los efectos a tono.', conVoz: true },
  { texto: 'Cambia la música', pide: 'Cambia la música por otra distinta que le vaya al video, y ajusta los efectos de sonido a ella.', conVoz: true },
  { texto: 'Cambia el final', pide: 'Cambia el final: haz otro cierre, que remate mejor el video.' }
]
/** No pisa la actual: el servidor pasa el hilo a una carpeta nueva y se lo dice al agente (`otraVersion` en etapas.ts). */
const VERSION = 'Haz otra versión'

/** El nombre de un video en su botón: `video-vertical.mp4` es «vertical». */
const etiqueta = (f: VideoFinal) => (f.ruta.split('/').pop() ?? f.ruta).replace(/\.mp4$/i, '').replace(/^video-/, '')

export function Final({ session, card, carpeta, finales }: { session: SessionMeta; card: Card; carpeta: string; finales: VideoFinal[] }) {
  const [pedido, setPedido] = useState('')
  const [error, setError] = useState('')
  const [snowEstado, setSnowEstado] = useState<string | null>(null)
  const trabaja = session.running || !!session.background?.length || !!session.pendiente
  // El pedido se queda marcado hasta que el agente se pone a trabajar en él.
  useEffect(() => {
    if (trabaja) setPedido('')
  }, [trabaja])
  // En El Diff la voz la graba el usuario: lo que cambiaría lo que se dice pediría grabarla otra vez.
  const narrado = !!card.editor
  const cambios = CAMBIOS.filter((c) => !narrado || c.conVoz)

  const sep = carpeta.includes('\\') ? '\\' : '/'
  const rutaAbsoluta = (r: string) => `${carpeta}${sep}${r.replaceAll(/[\\/]/g, sep)}`

  async function pedir(texto: string, hacer: () => Promise<unknown>) {
    setPedido(texto)
    setError('')
    try {
      await hacer()
    } catch (e) {
      setPedido('')
      setError(e instanceof Error ? e.message : String(e))
    }
  }

  async function despacharTelegram(f: VideoFinal) {
    setSnowEstado('Despachando a Telegram…')
    setError('')
    try {
      const res = await api<{ success: boolean; salida?: string }>('/api/snow/telegram-dispatch', {
        tipo: 'video',
        archivo: rutaAbsoluta(f.ruta),
        caption: `🎬 ${session.title}\nGenerado con Snow Studio 60fps`
      })
      setSnowEstado(res.success ? '¡Despachado a Telegram con éxito!' : 'Error despachando a Telegram')
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      setSnowEstado(null)
    }
  }

  async function subirYoutubeCdp(f: VideoFinal) {
    setSnowEstado('Subiendo a YouTube Studio (CDP Autónomo)…')
    setError('')
    try {
      const res = await api<{ success: boolean; salida?: string }>('/api/snow/youtube-upload', {
        video: rutaAbsoluta(f.ruta),
        title: session.title,
        desc: `${session.title}\n\nCreado y renderizado autónomamente con Snow Studio.\n#Shorts #SnowStudio`,
        visibility: 'PUBLIC'
      })
      setSnowEstado(res.success ? '¡Publicado en YouTube Studio con éxito!' : 'Fallo en subida CDP')
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      setSnowEstado(null)
    }
  }

  const mandar = (c: (typeof CAMBIOS)[number]) =>
    pedir(c.texto, () => api(`/api/sessions/${session.id}/send`, { text: `${c.pide}${narrado ? ' La voz no se toca.' : ''} Cuando acabes, vuelve a renderizar el video final.` }))
  const src = (f: VideoFinal) => `/api/sessions/${session.id}/archivo?ruta=${encodeURIComponent(f.ruta)}&t=${Math.round(f.t)}&descarga=${encodeURIComponent(f.nombre)}`
  const abrir = (ruta: string) => api('/api/open', { path: ruta }).catch((e) => setError(e.message))
  if (!finales.length) return null

  return (
    <section className="final">
      <div className="final-titulo">{finales.length > 1 ? 'Videos terminados' : 'Video terminado'}</div>
      <div className="final-fila">
        {finales.map((f, k) => (
          <a key={f.ruta} className={`final-boton ${k ? '' : 'principal'}`} href={src(f)} download={f.nombre} title={`Bajarlo como «${f.nombre}»`}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 4v11m0 0-4.5-4.5M12 15l4.5-4.5M5 19h14" />
            </svg>
            Descargar{finales.length > 1 ? ` ${etiqueta(f)}` : ''}
          </a>
        ))}
        {finales.map((f) => (
          <button key={`telegram:${f.ruta}`} className="final-boton telegram" disabled={trabaja || !!snowEstado} onClick={() => despacharTelegram(f)} title="Enviar video por Telegram a @CloudhermesnowBot">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.52 2.77-1.18 3.35-1.39 3.73-1.39.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/>
            </svg>
            Telegram
          </button>
        ))}
        {finales.map((f) => (
          <button key={`cdp:${f.ruta}`} className="final-boton cdp" disabled={trabaja || !!snowEstado} onClick={() => subirYoutubeCdp(f)} title="Publicar automáticamente en YouTube Studio mediante CDP sin cuotas">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/>
            </svg>
            Publicar (CDP)
          </button>
        ))}
        {finales.map((f) => <YoutubeBoton key={`youtube:${f.ruta}`} nombre={finales.length > 1 ? etiqueta(f) : undefined} disabled={trabaja} video={{ cardId: card.id, ruta: rutaAbsoluta(f.ruta), titulo: session.title }} />)}
        <button className="final-boton" title={carpeta} onClick={() => abrir(rutaAbsoluta(finales[0].ruta))}>
          <CarpetaIcono />
          Ver en la carpeta
        </button>
      </div>
      {snowEstado && <div className="final-estado-snow">⚡ {snowEstado}</div>}
      <div className="final-cambios">
        <span className="muted small">¿Algún cambio?</span>
        {cambios.map((c) => (
          <button key={c.texto} className={pedido === c.texto ? 'on' : ''} disabled={trabaja || !!pedido} onClick={() => mandar(c)}>
            {c.texto}
          </button>
        ))}
        {!narrado && (
          <button
            className={pedido === VERSION ? 'on' : ''}
            disabled={trabaja || !!pedido}
            title="La hace en una carpeta nueva junto a esta: la versión de ahora se queda como está"
            onClick={() => pedir(VERSION, () => api(`/api/sessions/${session.id}/version`, {}))}
          >
            {VERSION}
          </button>
        )}
        {trabaja && <span className="muted small">El agente está trabajando: cuando termine, puedes pedir otro.</span>}
      </div>
      {error && <span className="bad small">{error}</span>}
    </section>
  )
}

const CarpetaIcono = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
  </svg>
)
