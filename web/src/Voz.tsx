import { useEffect, useState } from 'react'
import type { Card, EstadoVoz } from '../../shared/types'
import { lineaVoz } from '../../shared/voz'
import { api } from './api'
import { Picker } from './Composer'
import { Logo } from './Logos'

/**
 * Voces Neurales Ultrarrápidas de Edge-TTS (Zero-Dependency & Timestamps en <3s).
 * No requieren cuenta ni suscripción.
 */
export const VOCES_NEURALES_RAPIDAS = [
  { id: 'edge:es-ES-AlvaroNeural', nombre: 'Álvaro (España)', descripcion: 'Enérgico · Noticiero y Edición Dinámica' },
  { id: 'edge:es-MX-DaliaNeural', nombre: 'Dalia (México)', descripcion: 'Cálida · Explicativa y Frutinovelas' },
  { id: 'edge:es-ES-ElviraNeural', nombre: 'Elvira (España)', descripcion: 'Suave · Documental y Reflexión' },
  { id: 'edge:es-MX-JorgeNeural', nombre: 'Jorge (México)', descripcion: 'Grave · Corporativo y Ventas' }
]

export interface VozClonada {
  id: string
  name: string
  refAudio: string
  created: string
  samplePath: string
  tier: string
}

/** El estado de la voz en Google AI Studio y biblioteca local. */
export function useVoz() {
  const [estado, setEstado] = useState<EstadoVoz>()
  const [vocesClonadas, setVocesClonadas] = useState<VozClonada[]>([])
  const [error, setError] = useState<string>()

  const recibir = (p: Promise<EstadoVoz>) => p.then((e) => (setEstado(e), setError(undefined)), (e: Error) => setError(e.message))

  const cargarBiblioteca = () => {
    fetch('/api/voz/biblioteca')
      .then((r) => r.json())
      .then((data) => Array.isArray(data) && setVocesClonadas(data))
      .catch(() => {})
  }

  useEffect(() => {
    void recibir(api('/api/voz'))
    cargarBiblioteca()
  }, [])

  useEffect(() => {
    if (!estado?.conectando) return
    const t = setInterval(() => void recibir(api('/api/voz')), 2000)
    return () => clearInterval(t)
  }, [estado?.conectando])

  return {
    estado,
    vocesClonadas,
    error: error ?? estado?.error,
    recargarBiblioteca: cargarBiblioteca,
    conectar: () => void recibir(api('/api/voz/conectar', {})),
    desconectar: () =>
      api<EstadoVoz>('/api/voz/desconectar', {}).then(
        (e) => void (setEstado(e), setError(undefined)),
        (x: Error) => {
          setError(x.message)
          throw x
        }
      )
  }
}

export type UsoVoz = ReturnType<typeof useVoz>

/** La opción del menú que conecta la cuenta de Google. */
const CONECTAR = ' conectar'
const CLONAR_NUEVA = ' clonar_nueva'

/**
 * El menú «Voz» del compositor de un video:
 * 1. La mando yo / Propia del estilo
 * 2. Voces Neurales Rápidas Edge-TTS (<3s, con timestamps)
 * 3. Voces Clonadas Locales (Zero-Shot)
 * 4. Voces de AI Studio (Google Flash TTS)
 */
export function SelectorVoz({ card, voz, valor, onCambio }: { card: Card; voz: UsoVoz; valor: string; onCambio(voz: string): void }) {
  if (card.voz === false) return null
  const e = voz.estado
  const propia = card.voz?.propia ?? 'La mando yo'

  let label = `Voz: ${propia.toLowerCase()}`
  if (valor) {
    if (valor.startsWith('edge:')) {
      const v = VOCES_NEURALES_RAPIDAS.find((x) => x.id === valor)
      label = `Voz: ${v?.nombre ?? valor} · Edge-TTS (<3s)`
    } else if (valor.startsWith('clonada:')) {
      const id = valor.replace('clonada:', '')
      const c = voz.vocesClonadas.find((x) => x.id === id)
      label = `Voz Clonada: ${c?.name ?? id}`
    } else if (e?.cuenta) {
      label = `Voz: ${valor} · AI Studio`
    }
  }

  return (
    <Picker
      label={label}
      value={valor}
      menuWidth={360}
      groups={[
        { label: 'Voz Propia', options: [{ value: '', label: propia }] },
        {
          label: ' TTS Ultrarrápido Neural (Sin Cuenta, Timestamps en <3s)',
          options: VOCES_NEURALES_RAPIDAS.map((v) => ({
            value: v.id,
            label: `${v.nombre} · ${v.descripcion}`
          }))
        },
        ...(voz.vocesClonadas.length > 0
          ? [
              {
                label: ' Voces Clonadas Locales (Zero-Shot)',
                options: voz.vocesClonadas.map((c) => ({
                  value: `clonada:${c.id}`,
                  label: `${c.name} (${c.tier})`
                }))
              }
            ]
          : []),
        ...gruposDeVocesAIStudio(e, valor)
      ]}
      onChange={(v) => {
        if (v === CONECTAR) voz.conectar()
        else onCambio(v)
      }}
    />
  )
}

function gruposDeVocesAIStudio(e: EstadoVoz | undefined, valor = '') {
  if (!e?.cuenta) {
    return [
      {
        label: 'Google AI Studio · Gemini 3.8 Flash TTS',
        options: [{ value: CONECTAR, label: 'Conectar tu cuenta de Google…' }]
      }
    ]
  }
  const grupos = new Map<string, { value: string; label: string }[]>()
  for (const v of e.voces) {
    grupos.set(`AI Studio · ${v.grupo}`, [
      ...(grupos.get(`AI Studio · ${v.grupo}`) ?? []),
      { value: v.nombre, label: `${v.nombre} · ${v.descripcion}` }
    ])
  }
  if (valor && !valor.startsWith('edge:') && !valor.startsWith('clonada:') && !e.voces.some((v) => v.nombre === valor)) {
    grupos.set('AI Studio', [{ value: valor, label: valor }])
  }
  return [...grupos].map(([label, options]) => ({ label, options }))
}

const ULTIMA = 'voz-hilo'

/**
 * En la etapa que espera tu voz (`Etapas.tsx`):
 * Permite sintetizar al instante con Edge-TTS, una voz clonada o con AI Studio.
 */
export function GenerarVoz({ onGenerar }: { onGenerar(texto: string): Promise<void> }) {
  const voz = useVoz()
  const e = voz.estado
  const [elegida, setElegida] = useState(() => localStorage.getItem(ULTIMA) ?? VOCES_NEURALES_RAPIDAS[0].id)
  const [mandando, setMandando] = useState(false)

  const valor = elegida || VOCES_NEURALES_RAPIDAS[0].id

  return (
    <div className="generar-voz" style={{ display: 'flex', flexDirection: 'column', gap: 10, background: 'rgba(255,255,255,0.03)', padding: 14, borderRadius: 12 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
        <span style={{ fontSize: 13, fontWeight: 500 }}>
           O genera la locución con TTS neural instantáneo o tu voz clonada:
        </span>
        <Picker
          label={`Voz: ${valor.startsWith('edge:') ? VOCES_NEURALES_RAPIDAS.find((x) => x.id === valor)?.nombre ?? valor : valor}`}
          value={valor}
          menuWidth={360}
          groups={[
            {
              label: ' TTS Ultrarrápido (<3s, Timestamps precisos)',
              options: VOCES_NEURALES_RAPIDAS.map((v) => ({
                value: v.id,
                label: `${v.nombre} · ${v.descripcion}`
              }))
            },
            ...(voz.vocesClonadas.length > 0
              ? [
                  {
                    label: ' Voces Clonadas Locales',
                    options: voz.vocesClonadas.map((c) => ({
                      value: `clonada:${c.id}`,
                      label: c.name
                    }))
                  }
                ]
              : []),
            ...gruposDeVocesAIStudio(e, valor)
          ]}
          onChange={(v) => {
            if (v === CONECTAR) voz.conectar()
            else {
              localStorage.setItem(ULTIMA, v)
              setElegida(v)
            }
          }}
        />
        <button
          className="primary small"
          disabled={mandando}
          onClick={() => {
            setMandando(true)
            void onGenerar(`No la voy a grabar: genérala tú.\n\n${lineaVoz({}, valor)}`).finally(() => setMandando(false))
          }}
        >
          {mandando ? 'Generando audio…' : 'Generar Voz'}
        </button>
      </div>
      {voz.error && <span className="bad small">{voz.error}</span>}
    </div>
  )
}

/** Opciones → Voz: Motor de Clonación Local Zero-Shot + TTS Neural + AI Studio */
export function VozOpciones({ voz }: { voz: UsoVoz }) {
  const e = voz.estado
  const [modalClonar, setModalClonar] = useState(false)
  const [nombreVoz, setNombreVoz] = useState('')
  const [textoMuestra, setTextoMuestra] = useState('Bienvenidos a Neva Studio. Este video fue creado con automatización cinemática inteligente.')
  const [rutaAudioRef, setRutaAudioRef] = useState('')
  const [clonando, setClonando] = useState(false)
  const [resultadoClon, setResultadoClon] = useState<string | null>(null)
  const [errorClon, setErrorClon] = useState<string | null>(null)

  const ejecutarClonacion = async () => {
    if (!rutaAudioRef.trim() || !nombreVoz.trim()) {
      setErrorClon('Debes indicar la ruta del audio de referencia (15-30s) y bautizar tu voz.')
      return
    }
    setClonando(true)
    setErrorClon(null)
    setResultadoClon(null)
    try {
      const res = await api<{ name: string; audioPath: string; elapsedSeconds: number }>('/api/voz/clonar', {
        refAudio: rutaAudioRef.trim(),
        name: nombreVoz.trim(),
        text: textoMuestra.trim()
      })
      setResultadoClon(`¡Voz «${res.name}» clonada con éxito en ${res.elapsedSeconds.toFixed(1)} segundos!`)
      voz.recargarBiblioteca()
    } catch (err: any) {
      setErrorClon(err?.message || String(err))
    } finally {
      setClonando(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* 1. Motor de Clonación Local Zero-Shot (Sprint 3.1) */}
      <div className="item" style={{ borderLeft: '3px solid #8b5cf6' }}>
        <div className="fila">
          <div style={{ fontSize: 22, marginRight: 8 }}></div>
          <div className="fila-nombre">
            <strong style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              Clonador de Voz Local Zero-Shot
              <span style={{ fontSize: 10, background: 'rgba(139, 92, 246, 0.2)', color: '#c084fc', padding: '2px 6px', borderRadius: 6, fontWeight: 700 }}>
                GAMA MEDIA (12GB RAM)
              </span>
            </strong>
            <span>
              Clona cualquier voz a partir de 15 a 30 segundos de audio. En tu equipo Gama Media con 12GB de RAM, clonar 1 minuto de locución toma ~2 minutos sin tocar la nube.
            </span>
          </div>
          <button className="primary small" onClick={() => setModalClonar(!modalClonar)}>
            {modalClonar ? 'Cerrar' : 'Clonar Nueva Voz'}
          </button>
        </div>

        {modalClonar && (
          <div style={{ marginTop: 14, padding: 16, background: 'rgba(255,255,255,0.03)', borderRadius: 12, border: '1px solid var(--line)', display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--accent)' }}>
              Configurar Clonación de Voz Local
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label className="small muted" style={{ display: 'block', marginBottom: 4 }}>
                  Nombre de la voz clonada:
                </label>
                <input
                  type="text"
                  className="input"
                  placeholder="Ej: Mi Voz Oficial, Locutor Documental"
                  value={nombreVoz}
                  onChange={(e) => setNombreVoz(e.target.value)}
                />
              </div>
              <div>
                <label className="small muted" style={{ display: 'block', marginBottom: 4 }}>
                  Ruta absoluta del audio de referencia (.wav o .mp3, 15-30s):
                </label>
                <input
                  type="text"
                  className="input mono"
                  placeholder="/home/snow/muestras/mi_voz_15s.wav"
                  value={rutaAudioRef}
                  onChange={(e) => setRutaAudioRef(e.target.value)}
                />
              </div>
            </div>
            <div>
              <label className="small muted" style={{ display: 'block', marginBottom: 4 }}>
                Texto de prueba inicial:
              </label>
              <textarea
                className="input"
                rows={2}
                value={textoMuestra}
                onChange={(e) => setTextoMuestra(e.target.value)}
              />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span className="small muted">
                Aviso: Tu equipo es Gama Media (12GB RAM): se optimiza la cuantización CPU para no saturar memoria.
              </span>
              <button className="primary" disabled={clonando} onClick={ejecutarClonacion}>
                {clonando ? 'Clonando (~2 min)...' : 'Clonar y Guardar en Biblioteca'}
              </button>
            </div>
            {resultadoClon && <span className="small" style={{ color: '#10b981', fontWeight: 600 }}>{resultadoClon}</span>}
            {errorClon && <span className="bad small">{errorClon}</span>}
          </div>
        )}

        {/* Voces clonadas existentes */}
        {voz.vocesClonadas.length > 0 && (
          <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {voz.vocesClonadas.map((vc) => (
              <span key={vc.id} style={{ fontSize: 12, padding: '4px 10px', background: 'rgba(255,255,255,0.06)', borderRadius: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                <span></span>
                <strong>{vc.name}</strong>
                <span className="muted" style={{ fontSize: 11 }}>({vc.tier})</span>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* 2. TTS Ultrarrápido Neural Edge-TTS (Sprint 3.2) */}
      <div className="item" style={{ borderLeft: '3px solid #10b981' }}>
        <div className="fila">
          <div style={{ fontSize: 22, marginRight: 8 }}></div>
          <div className="fila-nombre">
            <strong style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              TTS Ultrarrápido Neural (Sin Cuenta)
              <span style={{ fontSize: 10, background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', padding: '2px 6px', borderRadius: 6, fontWeight: 700 }}>
                ACTIVO & GRATIS
              </span>
            </strong>
            <span>
              Genera locuciones en español con entonación natural y archivo de timestamps sincronizado palabra por palabra en menos de 3 segundos, sin gastar saldo ni requerir logins.
            </span>
          </div>
          <span className="estado" style={{ color: '#10b981', fontWeight: 600 }}>● Disponible</span>
        </div>
      </div>

      {/* 3. Google AI Studio (Flash TTS) */}
      <div className="item">
        <div className="fila">
          <Logo de="gemini" />
          <div className="fila-nombre">
            <strong>Google AI Studio · Gemini 3.8 Flash TTS</strong>
            <span>
              {e?.cuenta
                ? `Conectado · ${e.voces.length} voces disponibles con tu cuenta de Google.`
                : 'Genera voces adicionales con Gemini 3.8 Flash conectando tu cuenta de Google.'}
            </span>
          </div>
          {e?.conectando ? (
            <span className="estado moviendo">Entra con Google en la ventana de {e.navegador}…</span>
          ) : e?.cuenta ? (
            <Picker
              className="acciones"
              label={<span className="estado">{e.cuenta}</span>}
              value=""
              groups={[{ label: 'Cuenta', options: [{ value: 'conectar', label: 'Volver a conectar' }, { value: 'desconectar', label: 'Desconectar' }] }]}
              onChange={(q) => (q === 'desconectar' ? void voz.desconectar().catch(() => {}) : voz.conectar())}
            />
          ) : (
            e && (
              <button className="primary" onClick={voz.conectar}>
                Conectar con Google
              </button>
            )
          )}
        </div>
        {e?.conectando && <p className="muted small fila-extra">Al entrar en {e.navegador}, la sesión pasa sola a Neva Studio.</p>}
        {voz.error && !e?.conectando && <p className="bad small fila-extra">{voz.error}</p>}
      </div>
    </div>
  )
}
