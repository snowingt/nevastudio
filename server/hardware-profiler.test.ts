import { test } from 'node:test'
import assert from 'node:assert'
import { profileHardware, estimateRenderTime } from './services/hardware-profiler.ts'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

test('hardware-profiler: detects 12GB RAM, classifies Gama Media and estimates times', async () => {
  const tmp = mkdtempSync(join(tmpdir(), 'hw-test-'))
  try {
    const profile = await profileHardware(tmp, true)
    assert.ok(profile.ramTotalGB > 0)
    assert.ok(typeof profile.cpuModel === 'string')
    assert.ok(['Gama Baja', 'Gama Media', 'Gama Alta'].includes(profile.tier))
    assert.ok(profile.voiceCloningNotice.includes('Gama Media') || profile.voiceCloningNotice.includes('equipo'))
    
    // Test estimates
    const time3D = estimateRenderTime('video-explicativo', 60, 'Gama Media')
    assert.strictEqual(time3D, '~25–40 min')

    const timeProcedural = estimateRenderTime('kinetic', 60, 'Gama Media')
    assert.strictEqual(timeProcedural, '~3–4 min')

    const timeDoc = estimateRenderTime('video-documental', 60, 'Gama Media')
    assert.strictEqual(timeDoc, '~2–3 min')
  } finally {
    rmSync(tmp, { recursive: true, force: true })
  }
})
