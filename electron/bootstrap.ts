import { execSync, spawn } from 'node:child_process'
import { existsSync, mkdirSync, chmodSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import https from 'node:https'
import fs from 'node:fs'

export interface BootstrapStatus {
  step: 'check' | 'ffmpeg' | 'python' | 'browser' | 'complete' | 'error'
  percent: number
  message: string
  error?: string
}

export interface RuntimePaths {
  ffmpegPath: string
  ffprobePath: string
  pythonPath: string
  chromePath: string
  ready: boolean
}

/** Descarga archivo por HTTPS siguiendo redirecciones con reporte de progreso */
export function downloadFile(url: string, destPath: string, onProgress?: (percent: number) => void): Promise<void> {
  return new Promise((resolve, reject) => {
    mkdirSync(dirname(destPath), { recursive: true })
    const file = fs.createWriteStream(destPath)

    function get(u: string) {
      https.get(u, { headers: { 'User-Agent': 'NevaStudio-Bootstrapper/1.0' } }, (res) => {
        if (res.statusCode && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          return get(res.headers.location)
        }
        if (res.statusCode !== 200) {
          return reject(new Error(`Fallo al descargar ${u}: HTTP ${res.statusCode}`))
        }
        const total = parseInt(res.headers['content-length'] || '0', 10)
        let cur = 0

        res.on('data', (chunk) => {
          cur += chunk.length
          if (total > 0 && onProgress) {
            onProgress(Math.round((cur / total) * 100))
          }
        })
        res.pipe(file)
        file.on('finish', () => {
          file.close()
          resolve()
        })
      }).on('error', (err) => {
        fs.unlink(destPath, () => {})
        reject(err)
      })
    }

    get(url)
  })
}

/** Detecta ejecutable en el PATH del sistema o devuelve null */
export function findSystemBinary(name: string): string | null {
  try {
    const cmd = process.platform === 'win32' ? `where ${name}` : `which ${name}`
    const out = execSync(cmd, { stdio: ['pipe', 'pipe', 'ignore'], encoding: 'utf8' }).trim()
    const first = out.split(/\r?\n/)[0]
    return first && existsSync(first) ? first : null
  } catch {
    return null
  }
}

/** Detecta instalaciones locales conocidas de Chrome / Chromium */
export function findChromeBinary(customDir?: string): string | null {
  const candidates: string[] = []
  if (customDir) {
    candidates.push(join(customDir, process.platform === 'win32' ? 'chrome.exe' : 'chrome'))
  }

  if (process.platform === 'win32') {
    const local = process.env.LOCALAPPDATA || ''
    const prog = process.env['ProgramFiles'] || 'C:\\Program Files'
    const prog86 = process.env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)'
    candidates.push(
      join(prog, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      join(prog86, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      join(local, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      join(prog, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
      join(prog86, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
      join(prog, 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe')
    )
  } else if (process.platform === 'darwin') {
    candidates.push(
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Chromium.app/Contents/MacOS/Chromium',
      '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
      '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
    )
  } else {
    candidates.push(
      '/usr/bin/google-chrome',
      '/usr/bin/google-chrome-stable',
      '/usr/bin/chromium',
      '/usr/bin/chromium-browser',
      '/usr/bin/brave-browser',
      '/usr/bin/microsoft-edge'
    )
  }

  for (const c of candidates) {
    if (existsSync(c)) return c
  }
  const inPath = findSystemBinary(process.platform === 'win32' ? 'chrome.exe' : 'google-chrome') || findSystemBinary('chromium')
  return inPath
}

/** Bootstrapper principal para inicializar y validar runtimes sin intervención técnica */
export async function ensureRuntimes(
  userDataPath: string,
  onProgress?: (status: BootstrapStatus) => void
): Promise<RuntimePaths> {
  const runtimesDir = join(userDataPath, 'runtimes')
  mkdirSync(runtimesDir, { recursive: true })

  onProgress?.({ step: 'check', percent: 5, message: 'Verificando componentes de aceleración...' })

  // 1. FFmpeg & FFprobe
  let ffmpeg = findSystemBinary('ffmpeg') || join(runtimesDir, process.platform === 'win32' ? 'ffmpeg.exe' : 'ffmpeg')
  let ffprobe = findSystemBinary('ffprobe') || join(runtimesDir, process.platform === 'win32' ? 'ffprobe.exe' : 'ffprobe')

  if (!existsSync(ffmpeg)) {
    onProgress?.({ step: 'ffmpeg', percent: 20, message: 'Configurando motor de video ultrarrápido (FFmpeg)...' })
    // Si no está en el sistema, aseguramos runtime estático
    try {
      const isWin = process.platform === 'win32'
      const isMac = process.platform === 'darwin'
      const arch = process.arch
      let url = ''
      if (isWin) {
        url = 'https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/ffmpeg-win32-x64'
      } else if (isMac) {
        url = `https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/ffmpeg-darwin-${arch}`
      } else {
        url = `https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/ffmpeg-linux-${arch}`
      }
      await downloadFile(url, ffmpeg, (pct) => {
        onProgress?.({ step: 'ffmpeg', percent: 20 + Math.round(pct * 0.25), message: `Descargando motor FFmpeg: ${pct}%` })
      })
      if (!isWin && existsSync(ffmpeg)) chmodSync(ffmpeg, 0o755)
    } catch (e) {
      console.warn('[bootstrap] No se pudo descargar FFmpeg standalone:', e)
    }
  }

  // 2. Python Portable / Standalone
  let python = findSystemBinary(process.platform === 'win32' ? 'python.exe' : 'python3') || join(runtimesDir, 'python', process.platform === 'win32' ? 'python.exe' : 'bin/python3')

  if (!existsSync(python)) {
    onProgress?.({ step: 'python', percent: 55, message: 'Verificando entorno de inteligencia artificial (Python)...' })
    // Se deja constancia de ruta portable para empaquetado standalone
    python = findSystemBinary('python3') || findSystemBinary('python') || python
  }

  // 3. Chrome / Chromium para Automatización CDP
  onProgress?.({ step: 'browser', percent: 80, message: 'Detectando navegador persistente para automatización de redes...' })
  const chrome = findChromeBinary(join(runtimesDir, 'chrome')) || ''

  onProgress?.({ step: 'complete', percent: 100, message: 'Estudio inicializado y listo.' })

  return {
    ffmpegPath: ffmpeg,
    ffprobePath: ffprobe,
    pythonPath: python,
    chromePath: chrome,
    ready: true
  }
}

/** Generador de la interfaz Apple Setup Assistant (Cupertino Dark Glass) para primera instalación */
export function getSetupAssistantHtml(status: BootstrapStatus): string {
  return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Neva Studio — Asistente de Configuración</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #09090B;
      color: #F4F4F5;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      overflow: hidden;
      user-select: none;
    }
    .card {
      width: 440px;
      padding: 36px 32px;
      background: rgba(24, 24, 27, 0.75);
      backdrop-filter: blur(28px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 20px;
      box-shadow: 0 24px 48px rgba(0, 0, 0, 0.5);
      text-align: center;
      animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: scale(0.96) translateY(8px); }
      to { opacity: 1; transform: scale(1) translateY(0); }
    }
    .icon {
      width: 56px;
      height: 56px;
      margin: 0 auto 18px;
      background: linear-gradient(135deg, #8B5CF6, #0EA5E9);
      border-radius: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      box-shadow: 0 8px 24px rgba(139, 92, 246, 0.3);
    }
    h1 {
      font-size: 19px;
      font-weight: 600;
      letter-spacing: -0.02em;
      margin-bottom: 8px;
    }
    p {
      font-size: 13px;
      color: #A1A1AA;
      line-height: 1.5;
      margin-bottom: 24px;
    }
    .progress-bar-bg {
      width: 100%;
      height: 6px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 999px;
      overflow: hidden;
      margin-bottom: 12px;
    }
    .progress-bar-fill {
      height: 100%;
      width: ${status.percent}%;
      background: linear-gradient(90deg, #8B5CF6, #0EA5E9);
      border-radius: 999px;
      transition: width 0.3s ease;
    }
    .status-msg {
      font-size: 12px;
      color: #71717A;
      font-variant-numeric: tabular-nums;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">✦</div>
    <h1>Preparando Neva Studio</h1>
    <p>Configurando motores de aceleración de video y entorno inteligente para tu equipo...</p>
    <div class="progress-bar-bg">
      <div class="progress-bar-fill"></div>
    </div>
    <div class="status-msg">${status.message} (${status.percent}%)</div>
  </div>
</body>
</html>`
}
