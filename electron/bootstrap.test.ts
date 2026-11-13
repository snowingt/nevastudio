import { test } from 'node:test'
import assert from 'node:assert'
import { ensureRuntimes, findChromeBinary, getSetupAssistantHtml } from './bootstrap.ts'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

test('bootstrap: checks runtimes and generates Apple setup assistant html', async () => {
  const tmp = mkdtempSync(join(tmpdir(), 'bootstrap-test-'))
  try {
    const statuses: any[] = []
    const paths = await ensureRuntimes(tmp, (st) => statuses.push(st))
    assert.ok(paths.ready)
    assert.ok(statuses.length > 0)

    const chrome = findChromeBinary()
    assert.ok(chrome === null || typeof chrome === 'string')

    const html = getSetupAssistantHtml({ step: 'ffmpeg', percent: 45, message: 'Descargando FFmpeg...' })
    assert.ok(html.includes('Neva Studio'))
    assert.ok(html.includes('45%'))
  } finally {
    rmSync(tmp, { recursive: true, force: true })
  }
})
