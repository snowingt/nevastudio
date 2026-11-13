import { useEffect, useState, type ReactNode } from 'react'
import { Icono } from './Iconos'
import { Logo } from './Logos'
import { CuentaAntigravity, CuentaChatGPT, CuentaClaude, CuentaOpenCode, Requisitos } from './Opciones'
import './Bienvenida.css'

const VISTA = 'bienvenida'
const EVENTO = 'sloth-bienvenida'

/** Todos los agentes, destacando Google Antigravity como primera opción recomendada. */
const OPCIONES = [
  {
    titulo: 'Motor de IA Recomendado',
    agentes: [
      ['antigravity', 'Google Antigravity (Gemini 2.5 & Claude Bridge)'],
    ]
  },
  {
    titulo: 'Otros agentes compatibles',
    agentes: [
      ['claude', 'Claude'],
      ['codex', 'ChatGPT'],
      ['opencode', 'OpenCode'],
      ['deepseek', 'DeepSeek'],
      ['gemini', 'Gemini'],
      ['cursor', 'Cursor'],
      ['muse', 'Muse Code'],
      ['pi', 'Pi']
    ]
  }
]

/** Opciones la vuelve a abrir. */
export const abrirBienvenida = () => dispatchEvent(new Event(EVENTO))

/**
 * La bienvenida: sale la primera vez que se abre Sloth y luego desde Opciones. Dice qué hace, qué hace falta (con lo
 * que falta a la vista, para hacerlo ahí mismo), cómo va un video, cuánto tarda y qué cuesta.
 */
export function Bienvenida() {
  const [abierta, setAbierta] = useState(() => !localStorage.getItem(VISTA))
  const [antigravity, setAntigravity] = useState<boolean>()
  const [claude, setClaude] = useState<boolean>()
  const [chatgpt, setChatgpt] = useState<boolean>()
  const [opencode, setOpencode] = useState<boolean>()
  const [listo, setListo] = useState<boolean>()
  // En la app instalada en Windows: si Neva Studio está anclada a la barra de tareas. `null`, aquí no se ofrece.
  const [anclada, setAnclada] = useState<boolean | null>(null)
  const [anclando, setAnclando] = useState(false)
  const [sinPermiso, setSinPermiso] = useState(false)

  useEffect(() => {
    const abrir = () => setAbierta(true)
    addEventListener(EVENTO, abrir)
    return () => removeEventListener(EVENTO, abrir)
  }, [])
  useEffect(() => {
    if (abierta) void window.sloth?.anclada().then(setAnclada, () => {})
  }, [abierta])
  useEffect(() => {
    if (!abierta) return
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && cerrar()
    addEventListener('keydown', onKey)
    return () => removeEventListener('keydown', onKey)
  }, [abierta])

  /** Windows pregunta en su ventana; si no deja pedirlo, se dice cómo hacerlo a mano. */
  async function anclar() {
    setAnclando(true)
    const r = await window.sloth!.anclar().catch(() => 'windows' as const)
    setAnclando(false)
    if (r === 'anclada') setAnclada(true)
    setSinPermiso(r === 'windows')
  }

  function cerrar() {
    localStorage.setItem(VISTA, '1')
    setAbierta(false)
  }

  if (!abierta) return null
  return (
    <div className="modal-backdrop" onClick={cerrar}>
      <div className="modal bienvenida" role="dialog" aria-modal aria-label="Bienvenida" onClick={(e) => e.stopPropagation()}>
        <header>
          <img src="/icon.svg" alt="" />
          <div>
            <h2>Te damos la bienvenida a Neva Studio</h2>
            <p>
              Neva Studio hace videos con Google Antigravity, Claude, ChatGPT, OpenCode y otros agentes. Eliges un estilo, le das un tema o un enlace, y
              lo ves trabajar paso a paso: investiga, escribe el guion, te pide tu voz y arma el video.
            </p>
          </div>
        </header>

        {/* Con uno basta. Con ChatGPT, además, hace las imágenes de los videos. */}
        <Paso n={1} titulo="Elige con qué trabaja" hecho={antigravity || claude || chatgpt || opencode}>
          Con uno basta, y Neva Studio no te cobra aparte. Puedes conectar Google Antigravity (Recomendado), o tus cuentas de Claude, ChatGPT u OpenCode.
          {OPCIONES.map(({ titulo, nota, agentes }: any) => (
            <div className="opcion" key={titulo}>
              <b>{titulo}</b>
              <div>
                <ul>
                  {agentes.map(([id, nombre]: any) => (
                    <li key={id}>
                      <Logo de={id} nombre={nombre} chico />
                      {nombre}
                    </li>
                  ))}
                </ul>
                {nota && <p>{nota}</p>}
              </div>
            </div>
          ))}
          <CuentaAntigravity onFalta={(falta) => setAntigravity(falta === undefined ? undefined : !falta)} />
          <CuentaClaude onFalta={(falta) => setClaude(falta === undefined ? undefined : !falta)} />
          <CuentaChatGPT onFalta={(falta) => setChatgpt(falta === undefined ? undefined : !falta)} />
          <CuentaOpenCode aviso onFalta={(falta) => setOpencode(falta === undefined ? undefined : !falta)} />
        </Paso>
        <Paso n={2} titulo="Prepara tu computadora" hecho={listo}>
          Los estilos usan unas herramientas (FFmpeg, Python…). Si falta alguna, aquí sale el botón para descargarla; tarda unos
          minutos y solo se hace una vez.
          <Requisitos onListo={setListo} />
        </Paso>
        {anclada !== null && (
          <Paso n={3} titulo="Ten Neva Studio a mano (opcional)" hecho={anclada}>
            {anclada ? 'Neva Studio está anclada a la barra de tareas.' : 'Ánclala a la barra de tareas para abrirla con un clic.'}
            {!anclada && (
              <div className="anclar">
                <button className="boton" disabled={anclando} onClick={() => void anclar()}>
                  {anclando ? 'Windows te pregunta…' : 'Anclar a la barra de tareas'}
                </button>
                {sinPermiso && (
                  <p className="small">
                    Windows no dejó anclarla desde aquí. Haz clic derecho en el icono de Neva Studio en la barra de tareas y elige
                    «Anclar a la barra de tareas».
                  </p>
                )}
              </div>
            )}
          </Paso>
        )}
        <Paso n={anclada === null ? 3 : 4} titulo="Haz tu primer video">
          Elige un estilo, escribe el tema o pega un enlace y pulsa <b>↑</b>. Cuando el guion está listo, Neva Studio te pide tu voz:
          grábalo con el celular y súbelo en la etapa «Tu voz». Luego arma el video y lo revisa. El Noticiero tarda de una a dos
          horas; el Video explicativo, unos 40 minutos. Cuando acaba, lo descargas desde el video o en «Mis videos».
        </Paso>
        <Paso n={anclada === null ? 4 : 5} titulo="Lo que gasta">
          Cada video usa una parte de los límites de tu plan, que ves en Opciones. Las cifras en dólares que salen en cada
          video dicen cuánto costaría pagado aparte, no lo que se te cobra. Un video gasta bastante: con el plan Pro el límite
          se acaba pronto, y con Max alcanza para varios. Con una llave de API no hay límites: esas cifras son lo que pagas.
          Con los modelos gratis de OpenCode no pagas nada, pero tu uso gratis tiene un tope, y es de tu computadora: al
          acabarse, vuelve solo en unas horas, y cambiar de cuenta no lo repone. Sus modelos de pago se cobran del saldo de tu
          cuenta de OpenCode.
        </Paso>

        <div className="modal-actions">
          <span className="muted small">La vuelves a ver en Opciones.</span>
          <button className="primary" autoFocus onClick={cerrar}>
            Empezar
          </button>
        </div>
      </div>
    </div>
  )
}

/** Un paso, con su número o, si ya está hecho, una palomita. */
function Paso({ n, titulo, hecho, children }: { n: number; titulo: string; hecho?: boolean; children: ReactNode }) {
  return (
    <section className={`paso${hecho ? ' hecho' : ''}`}>
      <span className="paso-n">{hecho ? <Icono de="palomita" /> : n}</span>
      <div className="paso-cuerpo">
        <strong>{titulo}</strong>
        <div className="paso-texto">{children}</div>
      </div>
    </section>
  )
}
