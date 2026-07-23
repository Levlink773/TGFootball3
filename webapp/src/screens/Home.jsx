import { useEffect, useState } from 'react'
import { claimGift, claimQuestBonus, claimQuests, getMatches, getPlayer, getQuests } from '../api'
import { useApi } from '../hooks'
import { Card, Loading, ErrorBox, NextBar, CtaButton, EnergyBar } from '../ui'
import { IconCalendar, IconBolt, IconUser, IconDumbbell, IconChat, IconShield, IconChart, IconTarget } from '../icons'
import { art } from '../assets/art'

// game community chat, same link the bot sends to new members
const CHAT_URL = import.meta.env.VITE_GAME_CHAT_URL || 'https://t.me/tgfootballchat'

function fmtTime(iso) {
  return new Date(iso).toLocaleString('uk-UA', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function fmtClock(iso) {
  return new Date(iso).toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
}

// Next occurrence of a league's registration/start day (day_start, 08:00)
function nextLeagueStart(dayStart) {
  const now = new Date()
  let d = new Date(now.getFullYear(), now.getMonth(), dayStart, 8, 0, 0)
  if (d <= now) d = new Date(now.getFullYear(), now.getMonth() + 1, dayStart, 8, 0, 0)
  return d
}

function fmtCountdown(ms) {
  if (ms <= 0) return '00:00:00'
  const total = Math.floor(ms / 1000)
  const d = Math.floor(total / 86400)
  const h = String(Math.floor((total % 86400) / 3600)).padStart(2, '0')
  const m = String(Math.floor((total % 3600) / 60)).padStart(2, '0')
  const s = String(total % 60).padStart(2, '0')
  return d > 0 ? `${d}д ${h}:${m}:${s}` : `${h}:${m}:${s}`
}

// 🏆 Активні турніри: countdown до реєстрації (неактивна ліга) чи до матчу (активна)
function TournamentsCard({ leagues, goTo }) {
  const [, tick] = useState(0)
  useEffect(() => {
    const t = setInterval(() => tick((n) => n + 1), 1000)
    return () => clearInterval(t)
  }, [])
  const now = Date.now()
  const rows = leagues.map((l) => {
    const target = l.is_active && l.next_match
      ? new Date(l.next_match.time_to_start)
      : nextLeagueStart(l.day_start)
    return {
      key: l.type,
      name: l.name,
      caption: l.is_active && l.next_match ? 'До матчу' : 'До реєстрації',
      left: target.getTime() - now,
    }
  })
  return (
    <Card>
      <div className="h-display text-sm text-white/80 mb-2">🏆 Активні турніри</div>
      <div className="space-y-2">
        {rows.map((r) => (
          <div key={r.key} className="flex items-center gap-2 cursor-pointer" onClick={() => goTo('league')}>
            <div className="h-display text-base flex-1">{r.name}</div>
            <div className="text-muted text-xs">{r.caption}</div>
            <div className="h-display text-lg text-neon glow-neon tabular-nums">{fmtCountdown(r.left)}</div>
          </div>
        ))}
      </div>
    </Card>
  )
}

// Щоденні завдання: 3 прогрес-рядки + кнопка нагороди
function DailyQuestsCard() {
  const quests = useApi(getQuests)
  const [claiming, setClaiming] = useState(false)
  const [gift, setGift] = useState(null)
  if (quests.loading || quests.error) return null
  const q = quests.data
  const openGift = async () => {
    setClaiming(true)
    try {
      const res = await claimGift()
      setGift(res)
      quests.reload()
    } catch { quests.reload() } finally {
      setClaiming(false)
    }
  }
  const claimTask = async (key) => {
    setClaiming(true)
    try {
      await (key === '__bonus' ? claimQuestBonus() : claimQuests(key))
      quests.reload()
    } catch { quests.reload() } finally {
      setClaiming(false)
    }
  }
  return (
    <Card accent="gold">
      <div className="h-display text-sm text-white/80 mb-2">Щоденні завдання</div>
      <div className="space-y-1.5">
        {q.quests.map((item) => {
          const done = item.current >= item.target
          return (
            <div key={item.key} className="flex items-center gap-2">
              <span className={done ? 'text-neon' : 'text-muted'}>{done ? '✅' : '⬜'}</span>
              <span className={`text-sm flex-1 ${item.claimed ? 'text-white/60 line-through' : ''}`}>{item.title}</span>
              {item.claimable ? (
                <CtaButton color="gold" onClick={() => claimTask(item.key)} disabled={claiming}>
                  Забрати ⚡{item.reward_energy}
                </CtaButton>
              ) : (
                <>
                  <span className="text-neon text-xs">⚡{item.reward_energy}</span>
                  <span className="h-display text-base tabular-nums">
                    {item.claimed ? '✓' : `${Math.min(item.current, item.target)}/${item.target}`}
                  </span>
                </>
              )}
            </div>
          )
        })}
      </div>

      {/* Бонус за всі три завдання */}
      {q.bonus_claimable && (
        <div className="mt-3">
          <CtaButton color="gold" onClick={() => claimTask('__bonus')} disabled={claiming}>
            Бонус за всі завдання · {q.bonus_coins} 💰
          </CtaButton>
        </div>
      )}
      {q.bonus_claimed && (
        <div className="text-muted text-xs mt-2">Бонус {q.bonus_coins} 💰 отримано ✓</div>
      )}

      {/* Щоденний подарунок — модуль зі скетчу Max 23.07 */}
      <div className="mt-3 pt-3 border-t border-white/10 flex items-center gap-3">
        <span className="text-2xl">🎁</span>
        <div className="flex-1">
          <div className="h-display text-sm">Щоденний подарунок</div>
          {gift && <div className="text-neon text-xs">+{gift.coins} 💰 · +{gift.energy} ⚡</div>}
        </div>
        {q.gift_claimed || gift ? (
          <span className="text-muted text-xs">{gift ? 'Отримано ✓' : 'Завтра знову 🎁'}</span>
        ) : (
          <CtaButton color="gold" onClick={openGift} disabled={claiming}>Забрати</CtaButton>
        )}
      </div>
    </Card>
  )
}

// ВІП-чип: активний — «ВІП до DD.MM», інакше — заклик придбати (перки коротко). Веде в магазин.
function VipChip({ vipActive, vipUntil, goTo }) {
  if (vipActive) {
    const until = vipUntil
      ? new Date(vipUntil).toLocaleDateString('uk-UA', { day: 'numeric', month: 'short' })
      : null
    return (
      <button
        onClick={() => goTo('shop')}
        className="w-full flex items-center gap-2 bg-card rounded-xl border border-gold/50 ring-glow-gold px-3 py-2"
      >
        <span className="text-lg">⚜️</span>
        <span className="h-display text-sm text-gold flex-1 text-left">ВІП активний{until ? ` · до ${until}` : ''}</span>
        <span className="text-muted text-xs">Продовжити ›</span>
      </button>
    )
  }
  return (
    <button
      onClick={() => goTo('shop')}
      className="w-full flex items-center gap-2 bg-card rounded-xl border border-gold/40 px-3 py-2"
    >
      <span className="text-lg">⚜️</span>
      <span className="h-display text-sm text-gold flex-1 text-left">Отримати ВІП</span>
      <span className="text-muted text-[11px] text-right">+300⚡ · +5% трен · x2 ›</span>
    </button>
  )
}

// «Почати тренування» / якщо треня йде — живий таймер до завершення (Max 23.07).
function TrainingCta({ training, goTo }) {
  const [, tick] = useState(0)
  const active = Boolean(training?.in_training && training?.training?.ends_at)
  useEffect(() => {
    if (!active) return
    const t = setInterval(() => tick((n) => n + 1), 1000)
    return () => clearInterval(t)
  }, [active])
  let label = 'Почати тренування ›'
  if (active) {
    const leftMs = new Date(training.training.ends_at).getTime() - Date.now()
    label = `Тренування · ${fmtCountdown(leftMs)} ›`
  }
  return (
    <CtaButton onClick={() => goTo('training')} className="w-full">
      {label}
    </CtaButton>
  )
}

// Головна (стадіон) — стартовий екран: банер → наступний матч → бліц → швидкі переходи.
export default function Home({ goTo, training }) {
  const player = useApi(getPlayer)
  const matches = useApi(getMatches)

  if (player.loading || matches.loading) return <Loading />
  if (player.error) return <ErrorBox error={player.error} onRetry={player.reload} />
  if (matches.error) return <ErrorBox error={matches.error} onRetry={matches.reload} />

  const nextMatch = matches.data.leagues.map((l) => l.next_match).find(Boolean)
  const blitz = matches.data.blitz.next
  const energyMax = player.data.vip_active ? 300 : 150

  return (
    <div className="p-4 space-y-4 relative">
      <div className="text-center pt-1 pb-2">
        <div className="h-display text-4xl text-gold glow-gold leading-none">TG Football</div>
        <div className="text-muted text-sm mt-1.5">Привіт, {player.data.name}!</div>
      </div>

      <VipChip vipActive={player.data.vip_active} vipUntil={player.data.vip_until} goTo={goTo} />

      {art['banner-home'] && (
        <img src={art['banner-home']} alt="" className="w-full aspect-[21/9] object-cover rounded-2xl border border-white/10" />
      )}

      {/* Next league match — frame 1 bottom bar */}
      <Card accent="gold">
        <div className="flex items-center gap-3">
          <IconCalendar size={26} className="text-gold shrink-0" />
          <div className="flex-1">
            <div className="h-display text-sm text-white/80 leading-none">Наступний матч</div>
            {nextMatch ? (
              <div className="h-display text-3xl text-gold glow-gold leading-tight">
                {fmtClock(nextMatch.time_to_start)}
              </div>
            ) : (
              <div className="text-muted text-xs mt-1">Немає запланованих матчів</div>
            )}
          </div>
          <CtaButton onClick={() => goTo('matches')}>
            {nextMatch ? 'Готуватися до матчу ›' : 'До матчів ›'}
          </CtaButton>
        </div>
        {nextMatch && (
          <div className="text-muted text-xs mt-2 pl-9">
            vs {nextMatch.opponent_club_name || '—'} · {fmtTime(nextMatch.time_to_start)}
          </div>
        )}
      </Card>

      {/* Blitz */}
      <NextBar
        icon={<IconBolt size={22} />}
        label={blitz ? (blitz.registered ? 'Бліц · ти в грі ✓' : 'Бліц · реєстрація') : 'Бліц щодня'}
        time={blitz ? fmtClock(blitz.start_at) : matches.data.blitz.schedule.map((s) => s.time).join(' · ')}
        onClick={() => goTo('matches')}
      />

      <EnergyBar value={player.data.energy} max={energyMax} />

      <DailyQuestsCard />

      <TournamentsCard leagues={matches.data.leagues} goTo={goTo} />

      <TrainingCta training={training} goTo={goTo} />

      <div className="grid grid-cols-3 gap-3">
        <Card className="text-center py-3 cursor-pointer" onClick={() => goTo('player')}>
          <IconUser size={24} className="text-neon mx-auto mb-1" />
          <div className="h-display text-sm">Гравець</div>
        </Card>
        <Card className="text-center py-3 cursor-pointer" onClick={() => goTo('training')}>
          <IconDumbbell size={24} className="text-neon mx-auto mb-1" />
          <div className="h-display text-sm">Трен-ня</div>
        </Card>
        <Card className="text-center py-3 cursor-pointer" onClick={() => goTo('team')}>
          <IconShield size={24} className="text-neon mx-auto mb-1" />
          <div className="h-display text-sm">Команда</div>
        </Card>
        <Card className="text-center py-3 cursor-pointer" onClick={() => goTo('stats')}>
          <IconChart size={24} className="text-neon mx-auto mb-1" />
          <div className="h-display text-sm">Статистика</div>
        </Card>
        <Card className="text-center py-3 cursor-pointer" onClick={() => goTo('trainer')}>
          <IconTarget size={24} className="text-neon mx-auto mb-1" />
          <div className="h-display text-sm">Тренер</div>
        </Card>
        {CHAT_URL ? (
          <Card className="text-center py-3 cursor-pointer" onClick={() => {
            const tg = window.Telegram?.WebApp
            tg?.openTelegramLink ? tg.openTelegramLink(CHAT_URL) : window.open(CHAT_URL, '_blank')
          }}>
            <IconChat size={24} className="text-gold mx-auto mb-1" />
            <div className="h-display text-sm">Чат гри</div>
          </Card>
        ) : (
          <Card className="text-center py-3 opacity-40">
            <IconChat size={24} className="text-muted mx-auto mb-1" />
            <div className="h-display text-sm text-muted">Чат</div>
          </Card>
        )}
      </div>

    </div>
  )
}
