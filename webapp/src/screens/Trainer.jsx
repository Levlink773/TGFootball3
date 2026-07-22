import { useState } from 'react'
import { getTrainerSession, trainerJoin, trainerAnswer, trainerPickStat } from '../api'
import { useApi } from '../hooks'
import { Card, SectionTitle, Loading, ErrorBox, CtaButton } from '../ui'
import { art } from '../assets/art'

const STATS = [
  { key: 'technique', label: '🎯 Техніка' },
  { key: 'kicks', label: '🥋 Удари' },
  { key: 'ball_selection', label: '🛡️ Відбір' },
  { key: 'speed', label: '⚡ Швидкість' },
  { key: 'endurance', label: '🏃 Витривалість' },
]

function fmtTime(iso) {
  return new Date(iso).toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
}

export default function Trainer({ goTo }) {
  const { data, error, loading, reload } = useApi(getTrainerSession)
  const [game, setGame] = useState(null) // {step, score, direction, done, stat_points, energy}
  const [flash, setFlash] = useState(null) // 'hit' | 'miss'
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState(null)

  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  const join = async () => {
    setBusy(true)
    setMessage(null)
    try {
      const r = await trainerJoin()
      setGame({ step: r.step, score: r.score, direction: r.direction, done: false })
    } catch (e) {
      setMessage(e.message)
    } finally {
      setBusy(false)
    }
  }

  const answer = async (dir) => {
    if (busy || !game || game.done) return
    setBusy(true)
    try {
      const r = await trainerAnswer(dir)
      setFlash(r.correct ? 'hit' : 'miss')
      setTimeout(() => setFlash(null), 350)
      setGame({ step: r.step, score: r.score, direction: r.direction, done: r.done,
                stat_points: r.stat_points, energy: r.energy })
    } catch (e) {
      setMessage(e.message)
    } finally {
      setBusy(false)
    }
  }

  const pickStat = async (stat) => {
    setBusy(true)
    try {
      const r = await trainerPickStat(stat)
      setMessage(`✅ +${r.points} до «${STATS.find(s => s.key === stat)?.label}»`)
      setGame(null)
      reload()
    } catch (e) {
      setMessage(e.message)
    } finally {
      setBusy(false)
    }
  }

  const active = game || (data.in_session ? { step: data.step, score: data.score, direction: data.direction, done: data.done, stat_points: data.stat_points } : null)

  return (
    <div className="p-4 space-y-4">
      <button onClick={() => goTo('training')} className="text-muted text-sm">‹ До тренувань</button>

      <div className="text-center">
        <div className="h-display text-3xl text-neon glow-neon">Тренер (QTE)</div>
        <div className="text-muted text-xs mt-1">Повторюй напрямок якомога швидше — до 3 секунд = максимум балів</div>
      </div>

      {message && (
        <div className="text-sm text-gold border border-gold/40 ring-glow-gold rounded-xl p-3" role="status">{message}</div>
      )}

      {!active && (
        <Card accent="neon">
          {data.window?.is_open ? (
            <>
              <div className="text-sm mb-3">Сесія відкрита до <b className="text-neon">{fmtTime(data.window.end_at)}</b>. Вхід коштує 1 🔑.</div>
              <CtaButton className="w-full" disabled={busy} onClick={join}>
                {busy ? '…' : 'Почати (1 🔑)'}
              </CtaButton>
            </>
          ) : (
            <div className="text-muted text-sm">
              Зараз сесія закрита. Розклад: <b className="text-white/90">10:00 · 13:00 · 19:00</b> (вхід відкритий одну годину від початку).
            </div>
          )}
        </Card>
      )}

      {active && !active.done && (
        <Card accent="neon" className={flash === 'hit' ? 'ring-glow-neon' : flash === 'miss' ? 'border-red-500/70' : ''}>
          <div className="flex justify-between text-sm mb-3">
            <span>Крок <b className="text-neon">{active.step}</b>/10</span>
            <span>Рахунок <b className="text-gold">{active.score}</b></span>
          </div>
          <div className="text-center text-7xl py-6 select-none" aria-live="polite">{active.direction}</div>
          <div className="grid grid-cols-3 gap-2">
            {['↖️', '⬆️', '↗️', '⬅️', '⏺', '➡️', '↙️', '⬇️', '↘️'].map((d, i) =>
              d === '⏺' ? (
                <span key={i} />
              ) : (
                <button
                  key={i}
                  onClick={() => answer(d)}
                  disabled={busy}
                  aria-label={`Напрямок ${d}`}
                  className="text-3xl py-3 rounded-xl border border-neon/40 active:bg-neon/20 disabled:opacity-50"
                >
                  {d}
                </button>
              )
            )}
          </div>
        </Card>
      )}

      {active && active.done && (
        <Card accent="gold">
          <SectionTitle>Сесію завершено!</SectionTitle>
          <div className="text-sm mb-1">Рахунок: <b className="text-gold">{active.score}</b></div>
          {active.energy != null && <div className="text-sm mb-1">Енергія: <b className="text-neon">+{active.energy} ⚡</b></div>}
          <div className="text-sm mb-3">Обери характеристику для <b className="text-gold">+{active.stat_points}</b> очок:</div>
          <div className="grid grid-cols-2 gap-2">
            {STATS.map((s) => (
              <button
                key={s.key}
                onClick={() => pickStat(s.key)}
                disabled={busy}
                className="h-display text-sm rounded-xl px-3 py-2.5 border border-gold/50 text-left text-white/90 active:bg-gold/20 disabled:opacity-50"
              >
                {s.label}
              </button>
            ))}
          </div>
        </Card>
      )}

      {art['tut-3-training'] && !active && (
        <img src={art['tut-3-training']} alt="" className="w-full aspect-video object-cover rounded-2xl border border-white/10" />
      )}
    </div>
  )
}
