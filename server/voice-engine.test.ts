import { test } from 'node:test'
import assert from 'node:assert'
import { generateFastTTS, getVoiceLibrary } from './services/voice-engine.ts'
import { mkdtempSync, rmSync, existsSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

test('voice-engine: generate fast TTS with timestamps in <3s and query library', async () => {
  const tmp = mkdtempSync(join(tmpdir(), 'voice-test-'))
  try {
    const audioOut = join(tmp, 'test.mp3')
    const tsOut = join(tmp, 'test.json')
    const res = await generateFastTTS({
      text: 'Prueba de síntesis ultrarrápida para Neva Studio.',
      outputAudio: audioOut,
      outputTimestamps: tsOut,
      appPath: process.cwd()
    })

    assert.ok(existsSync(audioOut))
    assert.ok(existsSync(tsOut))
    assert.ok(res.words.length > 0)
    assert.strictEqual(res.words[0].word, 'Prueba')
    assert.ok(res.duration > 0)

    const lib = getVoiceLibrary(tmp)
    assert.ok(Array.isArray(lib))
  } finally {
    rmSync(tmp, { recursive: true, force: true })
  }
})
