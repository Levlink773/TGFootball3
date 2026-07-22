import { useEffect, useState } from 'react'
import { getTraining, startTraining, claimEducation } from '../api'
import { useApi, fmtCountdown } from '../hooks'
import { Card, SectionTitle, Loading, ErrorBox, CtaButton, Banner } from '../ui'
import { art } from '../assets/art'

const STATS = [
  { key: 'technique', label: '🎯 Техніка' },
  { key: 'kicks', label: '🥋 Удари' },
  { key: 'ball_selection', label: '🛡️ Відбір' },
  { key: 'speed', label: '⚡ Швидкість' },
  { key: 'endurance', label: '🏃 Витривалість' },
]
const DURATIONS = [
  { minutes: 30, cost: 10, chance: 35 },
  { minutes: 60, cost: 20, chance: 45 },
  { minutes: 90, cost: 40, chance: 55 },
  { minutes: 120, cost: 60, chance: 75 },
]

function Countdown({ seconds, onDone }) {
  const [left, setLeft] = useState(seconds)
  useEffect(() => {
    setLeft(seconds)
    const t = setInterval(() => setLeft((v) => {
      if (v <= 1) { clearInterval(t); onDone?.() }
      return Math.max(0, v - 1)
    }), 1000)
    return () => clearInterval(t)
  }, [seconds]) // eslint-disable-line react-hooks/exhaustive-deps
  return <span className="h-display text-neon glow-neon">{fmtCountdown(left)}</span>
}

export default function Training({ goTo }) {
  const { data, error, loading, reload } = useApi(getTraining)
  const [stat, setStat] = useState('technique')
  const [minutes, setMinutes] = useState(30)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState(null)

  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  const act = async (fn) => {
    setBusy(true)
    setMessage(null)
    try {
      const r = await fn()
      if (r.claimed) setMessage(`🎁 Отримано: +${r.exp} XP · +${r.coins} 💰 · +${r.energy} ⚡`)
      if (r.started) setMessage(`Тренування почалось! Шанс успіху ${r.chance}%`)
      reload()
    } catch (e) {
      setMessage(e.message)
    } finally {
      setBusy(false)
    }
  }

  const chosen = DURATIONS.find((d) => d.minutes === minutes)
  const canAfford = data.energy >= chosen.cost

  return (
    <div className="p-4 space-y-4">
      <Banner src={art['banner-training']}>
        <span className="h-display text-2xl text-gold glow-gold">Тренування</span>
      </Banner>

      {message && (
        <div className="text-sm text-gold border border-gold/40 ring-glow-gold rounded-xl p-3" role="status">
          {message}
        </div>
      )}

      {data.last_result && (
        <Card accent={data.last_result.success ? 'neon' : undefined}>
          {data.last_result.success ? (
            <div className="text-neon text-sm">
              ✅ Тренування завершено: +{data.last_result.points} до характеристики!
            </div>
          ) : (
            <div className="text-muted text-sm">😓 Тренування завершено — цього разу без прогресу. Спробуй ще!</div>
          )}
        </Card>
      )}

      {data.in_training && data.training ? (
        <Card accent="gold">
          <SectionTitle>🏋️ Триває тренування</SectionTitle>
          <div className="flex justify-between items-center">
            <div>
              <div className="text-sm">Тренуємо: <b>{data.training.stats && (STATS.find(s => s.key === data.training.stats)?.label || data.training.stats)}</b></div>
              <div className="text-muted text-xs">до завершення</div>
            </div>
            <Countdown seconds={data.training.seconds_left} onDone={reload} />
          </div>
        </Card>
      ) : (
        <Card accent="gold">
          <SectionTitle>🏋️ Нове тренування</SectionTitle>
          <div className="text-muted text-xs mb-2">Характеристика</div>
          <div className="grid grid-cols-2 gap-2 mb-3">
            {STATS.map((s) => (
              <button
                key={s.key}
                onClick={() => setStat(s.key)}
                aria-pressed={stat === s.key}
                className={`h-display text-sm rounded-xl px-3 py-2.5 border text-left ${
                  stat === s.key ? 'text-gold border-gold ring-glow-gold' : 'text-white/80 border-white/10'
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
          <div className="text-muted text-xs mb-2">Тривалість</div>
          <div className="grid grid-cols-4 gap-2 mb-3">
            {DURATIONS.map((d) => (
              <button
                key={d.minutes}
                onClick={() => setMinutes(d.minutes)}
                aria-pressed={minutes === d.minutes}
                className={`rounded-xl px-1 py-2 border text-center ${
                  minutes === d.minutes ? 'text-neon border-neon ring-glow-neon' : 'text-white/80 border-white/10'
                }`}
              >
                <div className="h-display text-base">{d.minutes}хв</div>
                <div className="text-[10px] text-muted">⚡{d.cost} · {d.chance}%</div>
              </button>
            ))}
          </div>
          <CtaButton
            color="gold"
            className="w-full"
            disabled={busy || !canAfford}
            onClick={() => act(() => startTraining(stat, minutes))}
          >
            {busy ? '…' : canAfford ? `Почати (⚡${chosen.cost})` : `Мало енергії (потрібно ⚡${chosen.cost})`}
          </CtaButton>
        </Card>
      )}

      <Card>
        <SectionTitle accent="neon">🎯 Тренер (QTE)</SectionTitle>
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm">Ключі тренувань</span>
          <span className="h-display text-xl text-gold glow-gold">{data.training_keys}/3</span>
        </div>
        {data.trainer.joined_today && data.trainer.session_ended ? (
          <div className="text-sm mb-2">
            Сьогодні зіграно · рахунок: <b className="text-neon">{data.trainer.today_score}</b>
          </div>
        ) : null}
        <CtaButton className="w-full" onClick={() => goTo('trainer')}>
          Грати з тренером ›
        </CtaButton>
        <div className="text-muted text-[11px] mt-2 text-center">Сесії щодня: 10:00 · 13:00 · 19:00</div>
      </Card>

      <Card>
        <SectionTitle>🏫 Навчальний центр</SectionTitle>
        {data.education?.can_claim ? (
          <CtaButton color="gold" className="w-full" disabled={busy} onClick={() => act(claimEducation)}>
            🎁 Забрати нагороду
          </CtaButton>
        ) : data.education ? (
          <div className="flex justify-between items-center">
            <span className="text-muted text-sm">До наступної нагороди</span>
            <Countdown seconds={data.education.seconds_left} onDone={reload} />
          </div>
        ) : null}
      </Card>

      <Card>
        <div className="flex justify-between items-center">
          <span className="text-muted text-sm">⚡ Енергія</span>
          <span className="h-display text-xl text-neon">{data.energy}</span>
        </div>
      </Card>
    </div>
  )
}
