import { test } from 'node:test'
import assert from 'node:assert'
import { verifyGumroadLicense, getSavedLicense } from './services/gumroad-license.ts'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

test('gumroad-license: parse tier and save encrypted payload', async () => {
  const tmp = mkdtempSync(join(tmpdir(), 'gumroad-test-'))
  try {
    // Test with mock offline / dummy key
    const res = await verifyGumroadLicense('TEST-CREATOR-KEY-1234', tmp)
    assert.strictEqual(res.key, 'TEST-CREATOR-KEY-1234')
    assert.ok(['Creator', 'Marketer', 'Agency'].includes(res.tier))
    
    const saved = getSavedLicense(tmp)
    assert.ok(saved !== null)
    assert.strictEqual(saved?.key, 'TEST-CREATOR-KEY-1234')
  } finally {
    rmSync(tmp, { recursive: true, force: true })
  }
})
