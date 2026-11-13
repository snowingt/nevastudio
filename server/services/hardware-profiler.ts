import os from 'node:os'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import si from 'systeminformation'

export type HardwareTier = 'Gama Baja' | 'Gama Media' | 'Gama Alta'

export interface HardwareProfile {
  cpuModel: string
  cpuCores: number
  ramTotalGB: number
  ramFreeGB: number
  gpuModel: string
  hasNvidiaGpu: boolean
  hasDedicatedGpu: boolean
  tier: HardwareTier
  badge: string
  voiceCloningNotice: string
  renderTimeEstimates: Record<string, string>
  timestamp: string
}

export function estimateRenderTime(styleId: string, durationSec: number = 60, tier: HardwareTier = 'Gama Media'): string {
  const norm = styleId.toLowerCase()
  if (norm.includes('3d') || norm.includes('explicativo')) {
    if (tier === 'Gama Alta') return '~3–5 min'
    if (tier === 'Gama Media') return '~25–40 min'
    return '~60+ min (No recomendado)'
  }
  if (norm.includes('procedural') || norm.includes('kinetic') || norm.includes('reels') || norm.includes('xray')) {
    if (tier === 'Gama Alta') return '~1–2 min'
    if (tier === 'Gama Media') return '~3–4 min'
    return '~8–12 min'
  }
  if (norm.includes('documental') || norm.includes('collage') || norm.includes('sketch') || norm.includes('diff')) {
    if (tier === 'Gama Alta') return '~45–90 s'
    if (tier === 'Gama Media') return '~2–3 min'
    return '~5–7 min'
  }
  // Default / 2D / Canvas
  if (tier === 'Gama Alta') return '~30–60 s'
  if (tier === 'Gama Media') return '~1.5–2 min'
  return '~3–4 min'
}

export async function profileHardware(appPath: string = process.cwd(), forceRefresh: boolean = false): Promise<HardwareProfile> {
  const cachePath = join(appPath, 'data', 'hardware-profile.json')
  if (!forceRefresh && existsSync(cachePath)) {
    try {
      const cached = JSON.parse(readFileSync(cachePath, 'utf8')) as HardwareProfile
      return cached
    } catch { /* proceed to recalculate */ }
  }

  let cpuBrand = os.cpus()[0]?.model || 'CPU Desconocida'
  let cpuCores = os.cpus().length || 4
  let ramTotal = os.totalmem() / (1024 ** 3)
  let ramFree = os.freemem() / (1024 ** 3)
  let gpuModel = 'Gráfica Integrada'
  let hasNvidiaGpu = false
  let hasDedicatedGpu = false

  try {
    const [cpu, mem, graphics] = await Promise.all([
      si.cpu().catch(() => null),
      si.mem().catch(() => null),
      si.graphics().catch(() => null)
    ])

    if (cpu?.brand) cpuBrand = cpu.brand
    if (cpu?.cores) cpuCores = cpu.cores
    if (mem?.total) ramTotal = mem.total / (1024 ** 3)
    if (mem?.free) ramFree = mem.free / (1024 ** 3)

    if (graphics?.controllers && graphics.controllers.length > 0) {
      const gpus = graphics.controllers
      const nvidia = gpus.find(g => (g.vendor || '').toLowerCase().includes('nvidia') || (g.model || '').toLowerCase().includes('nvidia'))
      if (nvidia) {
        hasNvidiaGpu = true
        hasDedicatedGpu = true
        gpuModel = nvidia.model || 'NVIDIA Dedicated GPU'
      } else {
        const dedicated = gpus.find(g => (g.vram || 0) >= 1024 || (g.vendor || '').toLowerCase().includes('amd'))
        if (dedicated) {
          hasDedicatedGpu = true
          gpuModel = dedicated.model || 'AMD / Dedicated GPU'
        } else {
          gpuModel = gpus[0].model || 'Gráfica Integrada'
        }
      }
    }
  } catch (err) {
    console.warn('[hardware-profiler] Fallback a os nativo:', err)
  }

  let tier: HardwareTier = 'Gama Media'
  let badge = 'Gama Media (12GB–16GB)'
  let voiceNotice = 'Tu equipo es Gama Media: clonar 1 minuto de voz tomará ~2 minutos. Videos con diseño procedural tomarán ~3-4 min; videos 3D pesados tomarán ~25-40 min.'

  if (ramTotal < 8.5) {
    tier = 'Gama Baja'
    badge = 'Gama Baja (<8GB RAM)'
    voiceNotice = 'Aviso: Tu equipo es Gama Baja. Se recomienda usar voces ultrarrápidas en la nube (Edge-TTS / Gemini) y estilos 2D ligeros.'
  } else if (ramTotal >= 16 && (hasNvidiaGpu || hasDedicatedGpu)) {
    tier = 'Gama Alta'
    badge = 'Gama Alta (16GB+ RAM / GPU Dedicada)'
    voiceNotice = 'Rendimiento Turbo: Clonador de voz local ultra rápido (~30 segundos por minuto de audio) y aceleración por GPU habilitada.'
  } else {
    // 12GB - 16GB with integrated or entry GPU (User's machine: i7 + 12GB RAM)
    tier = 'Gama Media'
    badge = 'Gama Media (12GB RAM)'
    voiceNotice = 'Tu equipo es Gama Media: clonar 1 minuto de voz tomará ~2 minutos. Videos con diseño procedural tomarán ~3-4 min; videos 3D pesados tomarán ~25-40 min.'
  }

  const profile: HardwareProfile = {
    cpuModel: cpuBrand,
    cpuCores,
    ramTotalGB: Math.round(ramTotal * 10) / 10,
    ramFreeGB: Math.round(ramFree * 10) / 10,
    gpuModel,
    hasNvidiaGpu,
    hasDedicatedGpu,
    tier,
    badge,
    voiceCloningNotice: voiceNotice,
    renderTimeEstimates: {
      'video-documental': estimateRenderTime('video-documental', 60, tier),
      'video-el-diff': estimateRenderTime('video-el-diff', 60, tier),
      'video-explicativo': estimateRenderTime('video-explicativo', 60, tier),
      'reel-collage': estimateRenderTime('reel-collage', 60, tier),
      'kdrama-dominicana': estimateRenderTime('kdrama-dominicana', 60, tier),
      'becario-reels': estimateRenderTime('becario-reels', 60, tier),
      'collage-historia': estimateRenderTime('collage-historia', 60, tier),
      'kinetic': estimateRenderTime('kinetic', 60, tier)
    },
    timestamp: new Date().toISOString()
  }

  mkdirSync(dirname(cachePath), { recursive: true })
  writeFileSync(cachePath, JSON.stringify(profile, null, 2))
  return profile
}
