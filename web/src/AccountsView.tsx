import React, { useState, useEffect } from 'react'
import './cupertino-glass.css'

interface AccountStatus {
  platform: string
  name: string
  status: 'connected' | 'disconnected'
  profilePath: string
  encryptedWith: string
}

export function AccountsView() {
  const [accounts, setAccounts] = useState<AccountStatus[]>([
    { platform: 'youtube', name: 'YouTube Studio', status: 'connected', profilePath: '~/.nevastudio/vault/youtube', encryptedWith: 'safeStorage (AES-256)' },
    { platform: 'tiktok', name: 'TikTok Studio', status: 'connected', profilePath: '~/.nevastudio/vault/tiktok', encryptedWith: 'safeStorage (AES-256)' },
    { platform: 'meta', name: 'Meta Business Suite (IG/FB)', status: 'disconnected', profilePath: '~/.nevastudio/vault/meta', encryptedWith: 'safeStorage (AES-256)' }
  ])
  const [opening, setOpening] = useState<string | null>(null)

  const handleOpenBrowser = async (platform: string) => {
    setOpening(platform)
    try {
      // Abre Ghost Browser Vault para iniciar sesión o revisar cookies persistentes
      await fetch('/api/browser/open', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform })
      })
    } catch {
      // fallback
    } finally {
      setTimeout(() => setOpening(null), 2000)
    }
  }

  return (
    <div className="glass-panel" style={{ margin: '24px auto', maxWidth: 960, padding: 32 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 24, fontWeight: 700, letterSpacing: '-0.5px' }}>
             Bóveda de Cuentas y Navegador Fantasma (Ghost Browser Vault)
          </h2>
          <p style={{ margin: '6px 0 0 0', color: '#A1A1AA', fontSize: 14 }}>
            Sesiones persistentes con CDP, cifrado nativo <code>safeStorage</code> (AES-256) y perfiles blindados.
          </p>
        </div>
        <span className="glass-chip active" style={{ fontSize: 13, background: 'rgba(14, 165, 233, 0.15)', color: '#0EA5E9', border: '1px solid rgba(14, 165, 233, 0.3)' }}>
           safeStorage: Activo (Linux Secret Service / Keychain)
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {accounts.map((acc) => (
          <div
            key={acc.platform}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: 20,
              background: 'rgba(0,0,0,0.3)',
              border: '1px solid var(--glass-border)',
              borderRadius: 16
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 12,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background:
                    acc.platform === 'youtube' ? 'rgba(239, 68, 68, 0.15)' :
                    acc.platform === 'tiktok' ? 'rgba(16, 185, 129, 0.15)' :
                    'rgba(14, 165, 233, 0.15)',
                  fontSize: 20
                }}
              >
                {acc.platform === 'youtube' ? '' : acc.platform === 'tiktok' ? '' : ''}
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: 16, fontWeight: 600, color: '#F4F4F5' }}>{acc.name}</span>
                  <span
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      padding: '2px 8px',
                      borderRadius: 100,
                      background: acc.status === 'connected' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(113, 113, 122, 0.2)',
                      color: acc.status === 'connected' ? '#10B981' : '#71717A'
                    }}
                  >
                    {acc.status === 'connected' ? '● Sesión Activa' : '○ No Conectado'}
                  </span>
                </div>
                <div style={{ fontSize: 12, color: '#71717A', marginTop: 4 }}>
                  Perfil: <code>{acc.profilePath}</code> · Seguridad: {acc.encryptedWith}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: 10 }}>
              <button
                onClick={() => handleOpenBrowser(acc.platform)}
                disabled={opening === acc.platform}
                className="glass-button glass-button-secondary"
                style={{ padding: '8px 16px', fontSize: 13 }}
              >
                {opening === acc.platform ? 'Abriendo CDP...' : ' Abrir Navegador Seguro'}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 28, padding: 16, background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 12, fontSize: 13, color: '#A1A1AA', lineHeight: 1.6 }}>
        <strong style={{ color: '#F4F4F5' }}> Regla de Autenticación Invisible:</strong>
        <p style={{ margin: '6px 0 0 0' }}>
          Al abrir el navegador seguro, puedes iniciar sesión manualmente en la plataforma. Una vez completado el inicio de sesión, Neva Studio almacena las cookies cifradas. Todas las automatizaciones futuras se ejecutarán en segundo plano sin pedir contraseña ni código 2FA. Neva Studio jamás destruye la sesión gracias a la desconexión segura <code>browser.disconnect()</code>.
        </p>
      </div>
    </div>
  )
}
