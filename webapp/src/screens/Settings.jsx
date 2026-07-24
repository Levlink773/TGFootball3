import { useState } from 'react'
import { getSettings, updateSettings } from '../api'
import { useApi } from '../hooks'
import { Card, Loading, ErrorBox, Banner } from '../ui'
import { art } from '../assets/art'

function Toggle({ checked, onChange, disabled }) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={`w-12 h-7 rounded-full border transition-colors relative shrink-0 ${
        checked ? 'bg-neon/30 border-neon ring-glow-neon' : 'bg-card2 border-white/15'
      } disabled:opacity-40`}
    >
      <span
        className={`absolute top-0.5 w-5.5 h-5.5 rounded-full transition-all ${
          checked ? 'right-0.5 bg-neon shadow-[0_0_8px_rgba(0,255,255,0.8)]' : 'left-0.5 bg-white/40'
        }`}
        style={{ width: 22, height: 22 }}
      />
    </button>
  )
}

export default function Settings() {
  const { data, error, loading, reload } = useApi(getSettings)
  const [saving, setSaving] = useState(false)
  const [local, setLocal] = useState(null)

  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  const enabled = local ?? data.bot_buttons_enabled

  const toggle = async (next) => {
    setLocal(next)
    setSaving(true)
    try {
      await updateSettings(next)
    } catch {
      setLocal(!next) // revert on failure
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-4 space-y-4">
      <Banner src={art['banner-settings']}>
        <span className="h-display text-2xl text-gold glow-gold">Налаштування</span>
      </Banner>
      <Card>
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="h-display text-base">Кнопки бота</div>
            <div className="text-muted text-xs mt-0.5">
              Показувати ігрові кнопки в чаті з ботом. Вимкни, якщо граєш тільки в застосунку.
            </div>
          </div>
          <Toggle checked={enabled} onChange={toggle} disabled={saving} />
        </div>
      </Card>
      <div className="text-muted text-xs text-center">
        Зміни застосуються в боті після наступного повідомлення.
      </div>
    </div>
  )
}
