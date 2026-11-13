import { test } from 'node:test'
import assert from 'node:assert'
import { BatchFactory } from './batch-factory.ts'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

test('batch-factory: enqueue ideas and run sequential automation', async () => {
  const tmp = mkdtempSync(join(tmpdir(), 'batch-test-'))
  try {
    const factory = new BatchFactory(tmp)
    const items = factory.addItems([
      {
        title: 'Idea Test 1',
        topic: 'Ciberseguridad y Contraseñas',
        styleId: 'video-documental',
        platforms: ['tiktok', 'youtube']
      }
    ])

    assert.strictEqual(items.length, 1)
    assert.strictEqual(items[0].title, 'Idea Test 1')
    assert.ok(items[0].id.startsWith('batch_'))

    const q = factory.getQueue()
    assert.ok(q.length >= 1)
  } finally {
    rmSync(tmp, { recursive: true, force: true })
  }
})
