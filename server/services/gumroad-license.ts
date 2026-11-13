import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'

export type LicenseTier = 'Creator' | 'Marketer' | 'Agency'

export interface GumroadLicenseData {
  key: string
  tier: LicenseTier
  email: string
  valid: boolean
  verifiedAt: string
}

export async function verifyGumroadLicense(licenseKey: string, appPath: string = process.cwd()): Promise<GumroadLicenseData> {
  const cleanKey = licenseKey.trim()
  const res = await fetch('https://api.gumroad.com/v2/licenses/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ product_permalink: 'nevastudio', license_key: cleanKey })
  })
  const json = await res.json().catch(() => ({})) as any
  const purchase = json?.purchase || {}
  const rawTier = (purchase.variant || purchase.product_name || '').toLowerCase()
  const tier: LicenseTier = rawTier.includes('agency') ? 'Agency' : rawTier.includes('marketer') ? 'Marketer' : 'Creator'
  const licenseData: GumroadLicenseData = { key: cleanKey, tier, email: purchase.email || '', valid: !!json?.success, verifiedAt: new Date().toISOString() }

  const encPath = join(appPath, 'data', 'license.enc')
  mkdirSync(dirname(encPath), { recursive: true })
  let storage: any
  try {
    if (process.versions?.electron) {
      storage = (await import('electron')).safeStorage
    }
  } catch { /* Standalone Node fallback */ }
  const payload = Buffer.from(JSON.stringify(licenseData), 'utf8')
  const cipher = storage?.isEncryptionAvailable?.() ? storage.encryptString(payload.toString('utf8')) : payload
  writeFileSync(encPath, cipher)
  return licenseData
}

export function getSavedLicense(appPath: string = process.cwd()): GumroadLicenseData | null {
  const encPath = join(appPath, 'data', 'license.enc')
  if (!existsSync(encPath)) return null
  try {
    const raw = readFileSync(encPath)
    let storage: any
    try {
      if (process.versions?.electron) {
        storage = require('electron')?.safeStorage
      }
    } catch { /* Standalone Node */ }
    const text = storage?.isEncryptionAvailable?.() ? storage.decryptString(raw) : raw.toString('utf8')
    return JSON.parse(text) as GumroadLicenseData
  } catch { return null }
}
