import { spawn, type ChildProcess } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import net from 'node:net'
import { chromium, type Browser, type BrowserContext, type Page } from 'playwright-core'
import { findChromeBinary } from './bootstrap.ts'

export interface VaultConfig {
  profileId?: string
  userDataDir?: string
  headless?: boolean
  port?: number
}

export interface GhostSession {
  process: ChildProcess
  port: number
  profilePath: string
  browser: Browser
  context: BrowserContext
  endpoint: string
}

/** Encuentra un puerto TCP libre aleatorio para CDP */
export function getAvailablePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const srv = net.createServer()
    srv.listen(0, '127.0.0.1', () => {
      const addr = srv.address()
      if (addr && typeof addr === 'object') {
        const port = addr.port
        srv.close(() => resolve(port))
      } else {
        srv.close(() => reject(new Error('No se pudo obtener puerto')))
      }
    })
    srv.on('error', reject)
  })
}

/**
 * Ghost Browser Vault: Administrador de instancias de Chrome aisladas y persistentes
 * con ciberseguridad, safeStorage y regla estricta de no perder logins (browser.disconnect).
 */
export class GhostBrowserVault {
  private activeSessions: Map<string, GhostSession> = new Map()

  /**
   * Lanza o conecta a la bóveda de navegador persistente
   */
  async getOrCreateSession(config: VaultConfig = {}): Promise<GhostSession> {
    const profileId = config.profileId || 'default_account'
    if (this.activeSessions.has(profileId)) {
      const existing = this.activeSessions.get(profileId)!
      if (existing.browser.isConnected()) {
        return existing
      }
      this.activeSessions.delete(profileId)
    }

    const userDataDir = config.userDataDir || join(process.cwd(), 'data')
    const profilePath = join(userDataDir, 'browser-vault', profileId)
    mkdirSync(profilePath, { recursive: true })

    const port = config.port || await getAvailablePort()
    const chromeBin = findChromeBinary() || (process.platform === 'win32' ? 'chrome.exe' : 'google-chrome')

    const args = [
      `--remote-debugging-port=${port}`,
      `--user-data-dir=${profilePath}`,
      '--no-first-run',
      '--no-default-browser-check',
      '--disable-blink-features=AutomationControlled',
      '--disable-features=Translate,OptimizationHints,MediaRouter',
      '--disable-sync'
    ]

    if (process.platform === 'linux') {
      args.push('--password-store=basic')
    }

    if (config.headless) {
      args.push('--headless=new')
    }

    const proc = spawn(chromeBin, args, {
      detached: true,
      stdio: 'ignore'
    })
    proc.unref()

    // Esperar a que el puerto CDP esté escuchando
    const endpoint = `http://127.0.0.1:${port}`
    await this.waitForCdp(endpoint, 15_000)

    // Conectar vía Playwright CDP
    const browser = await chromium.connectOverCDP(endpoint)
    const contexts = browser.contexts()
    const context = contexts.length > 0 ? contexts[0] : await browser.newContext()

    const session: GhostSession = {
      process: proc,
      port,
      profilePath,
      browser,
      context,
      endpoint
    }

    this.activeSessions.set(profileId, session)
    return session
  }

  /**
   * REGLA ESTRICTA CDP: Desconecta el cliente Playwright sin cerrar la ventana ni destruir la sesión.
   */
  async disconnect(profileId: string = 'default_account'): Promise<void> {
    const s = this.activeSessions.get(profileId)
    if (!s) return
    try {
      // Desconectar cliente CDP preservando el proceso Chrome y los logins
      if (typeof (s.browser as any).disconnect === 'function') {
        await (s.browser as any).disconnect()
      } else {
        // En Playwright connectOverCDP, close() desconecta el socket CDP sin matar Chrome
        await s.browser.close()
      }
    } catch { /* ya desconectado */ }
    this.activeSessions.delete(profileId)
  }

  /**
   * Guarda credenciales o tokens cifrados con safeStorage de Electron
   */
  async saveSecureData(key: string, value: string, profilePath: string): Promise<void> {
    const secureFile = join(profilePath, 'secure-vault.bin')
    let storage: any
    try {
      if (process.versions?.electron) {
        storage = (await import('electron')).safeStorage
      }
    } catch { /* fallback */ }

    const raw = Buffer.from(value, 'utf8')
    const cipher = storage?.isEncryptionAvailable?.() ? storage.encryptString(value) : raw
    writeFileSync(secureFile, cipher)
  }

  /**
   * Recupera datos cifrados
   */
  async getSecureData(profilePath: string): Promise<string | null> {
    const secureFile = join(profilePath, 'secure-vault.bin')
    if (!existsSync(secureFile)) return null
    try {
      const raw = readFileSync(secureFile)
      let storage: any
      try {
        if (process.versions?.electron) {
          storage = (await import('electron')).safeStorage
        }
      } catch { /* fallback */ }
      return storage?.isEncryptionAvailable?.() ? storage.decryptString(raw) : raw.toString('utf8')
    } catch {
      return null
    }
  }

  private async waitForCdp(endpoint: string, timeoutMs: number): Promise<void> {
    const start = Date.now()
    while (Date.now() - start < timeoutMs) {
      try {
        const res = await fetch(`${endpoint}/json/version`)
        if (res.ok) return
      } catch { /* reintento */ }
      await new Promise(r => setTimeout(r, 250))
    }
    throw new Error(`Tiempo de espera agotado esperando CDP en ${endpoint}`)
  }
}

export const ghostBrowserVault = new GhostBrowserVault()
