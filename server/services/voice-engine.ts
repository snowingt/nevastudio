import { spawn } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'

export interface VoiceWordTimestamp {
  word: string
  start: number
  end: number
}

export interface TTSResult {
  text: string
  voice: string
  duration: number
  audioPath: string
  timestampsPath: string
  words: VoiceWordTimestamp[]
}

export interface ClonedVoiceEntry {
  id: string
  name: string
  refAudio: string
  created: string
  samplePath: string
  tier: string
}

export async function generateFastTTS(params: {
  text: string
  voice?: string
  outputAudio: string
  outputTimestamps: string
  rate?: string
  pythonBin?: string
  appPath?: string
}): Promise<TTSResult> {
  const app = params.appPath || process.cwd()
  const pyScript = join(app, 'python', 'procesos', 'tts_rapido.py')
  const py = params.pythonBin || (process.platform === 'win32' ? 'python.exe' : 'python3')
  const voice = params.voice || 'es-ES-AlvaroNeural'
  const rate = params.rate || '+0%'

  mkdirSync(dirname(params.outputAudio), { recursive: true })
  mkdirSync(dirname(params.outputTimestamps), { recursive: true })

  return new Promise((resolve, reject) => {
    const child = spawn(py, [
      pyScript,
      '--text', params.text,
      '--voice', voice,
      '--rate', rate,
      '--output-audio', params.outputAudio,
      '--output-timestamps', params.outputTimestamps
    ], { stdio: ['ignore', 'pipe', 'pipe'] })

    let stderr = ''
    child.stderr.on('data', d => { stderr += d.toString() })

    child.on('close', code => {
      if (code !== 0) {
        return reject(new Error(`tts_rapido.py falló con código ${code}: ${stderr}`))
      }
      try {
        const raw = readFileSync(params.outputTimestamps, 'utf8')
        const data = JSON.parse(raw)
        resolve({
          text: params.text,
          voice,
          duration: data.duration || 0,
          audioPath: params.outputAudio,
          timestampsPath: params.outputTimestamps,
          words: data.words || []
        })
      } catch (err) {
        reject(err)
      }
    })
  })
}

export async function cloneLocalVoice(params: {
  refAudio: string
  name: string
  text: string
  outputAudio: string
  speed?: number
  appPath?: string
  pythonBin?: string
}): Promise<{ name: string; audioPath: string; elapsedSeconds: number }> {
  const app = params.appPath || process.cwd()
  const pyScript = join(app, 'python', 'procesos', 'clonar_voz.py')
  const py = params.pythonBin || (process.platform === 'win32' ? 'python.exe' : 'python3')
  const libDir = join(app, 'data', 'voces')
  mkdirSync(libDir, { recursive: true })

  const t0 = Date.now()
  return new Promise((resolve, reject) => {
    const child = spawn(py, [
      pyScript,
      '--ref-audio', params.refAudio,
      '--name', params.name,
      '--text', params.text,
      '--output', params.outputAudio,
      '--speed', String(params.speed || 1.0),
      '--library-dir', libDir
    ], { stdio: ['ignore', 'pipe', 'pipe'] })

    let stderr = ''
    child.stderr.on('data', d => { stderr += d.toString() })

    child.on('close', code => {
      const elapsedSeconds = (Date.now() - t0) / 1000
      if (code !== 0) {
        return reject(new Error(`clonar_voz.py falló con código ${code}: ${stderr}`))
      }
      resolve({ name: params.name, audioPath: params.outputAudio, elapsedSeconds })
    })
  })
}

export function getVoiceLibrary(appPath: string = process.cwd()): ClonedVoiceEntry[] {
  const libFile = join(appPath, 'data', 'voces', 'biblioteca.json')
  if (!existsSync(libFile)) return []
  try {
    return JSON.parse(readFileSync(libFile, 'utf8')) as ClonedVoiceEntry[]
  } catch {
    return []
  }
}
