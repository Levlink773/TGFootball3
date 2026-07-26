import { useEffect, useState } from 'react'
import { claimGift, claimQuestBonus, claimQuests, getMatches, getPlayer, getQuests } from '../api'
import { useApi } from '../hooks'
import { Card, Loading, ErrorBox, CtaButton, EnergyBar } from '../ui'
import { IconCalendar, IconBolt, IconChat, IconShield, IconChart, IconTarget, IconGift, IconVipShield } from '../icons'
import { art } from '../assets/art'

// game community chat, same link the bot sends to new members
const CHAT_URL = import.meta.env.VITE_GAME_CHAT_URL || 'https://t.me/tgfootballchat'

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

// Енергія НЕ капає щохвилини — єдине поповнення це крон о 22:15, і він
// ВИСТАВЛЯЄ значення в кап, тобто нічого не робить тому, у кого вже більше.
// Тому підказку показуємо лише при energy < max, інакше таймер брехав би.
// ponytail: крон іде за часом сервера, відлік — за часом телефону; те саме
// припущення вже робить nextLeagueStart. Upgrade path: energy_reset_at з API.
function energyResetIn(now = new Date()) {
  const next = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 22, 15, 0)
  if (next <= now) next.setDate(next.getDate() + 1)
  return next.getTime() - now.getTime()
}

// Тік раз на 30 с: для багатогодинного відліку хвилинної точності досить,
// а на екрані вже два секундні таймери.
function EnergyBarWithHint({ value, max }) {
  const [, tick] = useState(0)
  const low = value < max
  useEffect(() => {
    if (!low) return
    const t = setInterval(() => tick((n) => n + 1), 30000)
    return () => clearInterval(t)
  }, [low])
  return (
    <EnergyBar
      value={value}
      max={max}
      hint={low ? `До поповнення ${fmtCountdown(energyResetIn())}` : null}
    />
  )
}

// Українська множина днів: 1 день · 2-4 дні · 5-20 днів · 21 день · 22 дні
function pluralDays(n) {
  const t = n % 10, h = n % 100
  if (t === 1 && h !== 11) return 'день'
  if (t >= 2 && t <= 4 && (h < 12 || h > 14)) return 'дні'
  return 'днів'
}

// ponytail: vip_until — наївний ISO з серверним часом, парситься як час телефону,
// те саме припущення вже робить nextLeagueStart для матчів. Стеля: гравець в іншій
// таймзоні побачить ±1 день. Upgrade path: віддавати offset-aware мітку з player_payload().
// floor, не ceil: гілка «менше доби» вже ловить <24 год, тож floor ніколи не
// покаже «0 днів», а ceil завищував би — при 1 добі й 1 хвилині малював «2 дні».
function vipLeftLabel(vipUntil) {
  if (!vipUntil) return null
  const ms = new Date(vipUntil).getTime() - Date.now()
  if (!(ms > 0)) return null           // ловить і NaN від битої дати
  if (ms < 86400000) return 'Дійсно ще менше доби'
  const d = Math.floor(ms / 86400000)
  return `Дійсно ще ${d} ${pluralDays(d)}`
}

function BonusCell({ Icon, value, label }) {
  return (
    <div>
      <div className="flex items-center justify-center gap-1">
        <Icon size={14} className="text-gold shrink-0" />
        <span className="h-display text-base text-white leading-none">{value}</span>
      </div>
      <div className="text-muted text-[10px] mt-0.5 leading-tight">{label}</div>
    </div>
  )
}

// ponytail: обидва стани носять одне золоте свічення — «пласко і не привертає
// уваги» це і був фідбек, який ця переробка чинить. Компонент навмисно
// самодостатній (нічого не винесено в ui.jsx), щоб зміна візуалу лишалась
// переписуванням однієї функції, а не археологією.
function VipCard({ vipActive, vipUntil, goTo }) {
  const left = vipActive ? vipLeftLabel(vipUntil) : null
  return (
    <Card accent="gold" onClick={() => goTo('shop')}>
      <div className="flex items-center gap-3">
        <IconVipShield
          size={38}
          className={`shrink-0 ${vipActive ? 'text-gold drop-shadow-[0_0_10px_rgba(255,215,0,0.55)]' : 'text-gold/50'}`}
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-baseline gap-1.5">
            <span className="h-display text-2xl text-gold glow-gold leading-none">VIP</span>
            <span className="h-display text-[11px] text-white/70 tracking-wider">
              {vipActive ? '• АКТИВНО' : '• НЕАКТИВНИЙ'}
            </span>
          </div>
          <div className="text-muted text-xs mt-1 truncate">
            {vipActive ? (left || 'Активний') : 'Відкрий усі бонуси'}
          </div>
        </div>
        <span className="text-muted text-xl leading-none shrink-0">›</span>
      </div>

      <div className="mt-3 pt-3 border-t border-white/10 grid grid-cols-3 gap-2 text-center">
        <BonusCell Icon={IconBolt} value="+300" label="енергії" />
        <BonusCell Icon={IconChart} value="+5%" label="тренування" />
        {/* x2 — це нагороди з НАВЧАЛЬНОГО ЦЕНТРУ (education_center.py:122-128),
            а не тренування. У макеті підписано помилково. */}
        <BonusCell Icon={IconGift} value="x2" label="навчання" />
      </div>
    </Card>
  )
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

// Рівень + прогрес до наступного (Max 26.07). Дані вже були в /api/player,
// головна їх просто ігнорувала. Живе на місці видаленого напису «TG Football»,
// що дублював липку шапку в App.jsx.
function LevelBar({ level, exp, expFloor, expNext }) {
  const max = expNext === null || expNext === undefined
  const span = max ? 1 : Math.max(expNext - expFloor, 1)
  const pct = max ? 100 : Math.min(100, Math.max(0, ((exp - expFloor) / span) * 100))
  return (
    <div className="flex items-center gap-2">
      <span className="h-display text-[11px] text-gold border border-gold/60 rounded-full px-2 py-0.5 shrink-0">
        LVL {level}
      </span>
      <div className="flex-1 h-2 rounded-full bg-card2 overflow-hidden">
        <div className="h-full bar-neon" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-muted text-[10px] tabular-nums shrink-0">
        {max ? 'МАКС' : `${exp}/${expNext}`}
      </span>
    </div>
  )
}

// Щоденний подарунок окремою картою НАД завданнями: раніше він був останнім
// рядком усередині DailyQuestsCard і губився під трьома завданнями (фідбек Max).
function GiftCard({ quests }) {
  const [claiming, setClaiming] = useState(false)
  const [gift, setGift] = useState(null)
  if (quests.loading || quests.error) return null
  const q = quests.data
  const done = q.gift_claimed || gift
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
  return (
    <Card accent="gold">
      <div className="flex items-center gap-3">
        <span className="text-4xl shrink-0">🎁</span>
        <div className="flex-1 min-w-0">
          <div className="h-display text-xl text-gold glow-gold leading-none">Щоденний подарунок</div>
          <div className="text-muted text-xs mt-1">
            {gift
              ? `+${gift.coins} 💰 · +${gift.energy} ⚡`
              : done ? 'Уже отримано — завтра знову 🎁' : 'Монети та енергія чекають на тебе'}
          </div>
        </div>
      </div>
      {!done && (
        <div className="mt-3">
          <CtaButton color="gold" onClick={openGift} disabled={claiming} className="w-full">
            Забрати подарунок
          </CtaButton>
        </div>
      )}
    </Card>
  )
}

// Щоденні завдання: 3 прогрес-рядки + кнопка нагороди
function DailyQuestsCard({ quests }) {
  const [claiming, setClaiming] = useState(false)
  if (quests.loading || quests.error) return null
  const q = quests.data
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
    </Card>
  )
}

// «Рекомендована дія» (Max 26.07): перше, що підходить, і стає підказкою.
// Замінює колишню TrainingCta — не додає блок, а робить наявний розумнішим.
function NextStepCta({ training, nextMatch, blitz, goTo }) {
  const [, tick] = useState(0)
  const active = Boolean(training?.in_training && training?.training?.ends_at)
  useEffect(() => {
    if (!active) return
    const t = setInterval(() => tick((n) => n + 1), 1000)
    return () => clearInterval(t)
  }, [active])

  // Подарунок навмисно НЕ в ланцюжку: він живе на цьому ж екрані, тож кнопка
  // вела б у нікуди. Його вже закривають велика картка нижче й бейдж навігації.
  let label = 'Прокачай гравця в магазині ›'
  let target = 'shop'

  if (nextMatch && !nextMatch.registered) {
    label = 'Зареєструйся на матч ›'; target = 'matches'
  } else if (blitz?.can_register && !blitz.registered) {
    label = 'Зареєструйся на бліц ›'; target = 'matches'
  } else if (training?.education?.can_claim) {
    label = 'Забери нагороду з навчального центру ›'; target = 'training'
  } else if (active) {
    const leftMs = new Date(training.training.ends_at).getTime() - Date.now()
    label = `Тренування · ${fmtCountdown(leftMs)} ›`; target = 'training'
    // Той самий предикат, що й бейдж навігації в App.jsx — щоб вони не розходились.
  } else if (training && !training.in_training && training.energy > 0) {
    label = 'Проведи тренування ›'; target = 'training'
  }

  return (
    <div>
      <div className="text-muted text-[10px] uppercase tracking-wider mb-1">Рекомендована дія</div>
      <CtaButton onClick={() => goTo(target)} className="w-full">
        {label}
      </CtaButton>
    </div>
  )
}

// Головна (стадіон) — стартовий екран: банер → наступний матч → бліц → швидкі переходи.
export default function Home({ goTo, training }) {
  const player = useApi(getPlayer)
  const matches = useApi(getMatches)
  // Піднято з DailyQuestsCard: тепер той самий запит живить і картку подарунка,
  // і завдання, і «рекомендовану дію» — замість трьох запитів на один ендпоінт.
  const quests = useApi(getQuests)

  if (player.loading || matches.loading) return <Loading />
  if (player.error) return <ErrorBox error={player.error} onRetry={player.reload} />
  if (matches.error) return <ErrorBox error={matches.error} onRetry={matches.reload} />

  const nextMatch = matches.data.leagues.map((l) => l.next_match).find(Boolean)
  const blitz = matches.data.blitz.next
  const energyMax = player.data.vip_active ? 300 : 150

  return (
    <div className="p-4 space-y-4 relative">
      {/* Напис «TG Football» тут дублював липку шапку App.jsx, видимую на цьому ж
          екрані. На його місці — рівень і прогрес гравця. */}
      <div className="pt-1 pb-1">
        <div className="text-muted text-sm mb-2">Привіт, {player.data.name}!</div>
        <LevelBar
          level={player.data.level}
          exp={player.data.exp}
          expFloor={player.data.exp_floor}
          expNext={player.data.exp_next}
        />
      </div>

      <NextStepCta training={training} nextMatch={nextMatch} blitz={blitz} goTo={goTo} />

      <VipCard vipActive={player.data.vip_active} vipUntil={player.data.vip_until} goTo={goTo} />

      {art['banner-home'] && (
        <img src={art['banner-home']} alt="" className="w-full aspect-[21/9] object-cover rounded-2xl border border-white/10" />
      )}

      {/* Наступний матч + Бліц — 2 колонки поруч (Max 24.07) */}
      <div className="grid grid-cols-2 gap-3">
        <Card accent="gold" onClick={() => goTo('matches')}>
          <div className="flex items-center gap-2 mb-1">
            <IconCalendar size={18} className="text-gold shrink-0" />
            <span className="h-display text-[11px] text-white/80 uppercase tracking-wider">Матч</span>
          </div>
          {nextMatch ? (
            <>
              <div className="h-display text-3xl text-gold glow-gold leading-none">{fmtClock(nextMatch.time_to_start)}</div>
              <div className="text-muted text-[10px] mt-1 truncate">vs {nextMatch.opponent_club_name || '—'}</div>
            </>
          ) : (
            <div className="text-muted text-xs">Немає матчів</div>
          )}
        </Card>
        <Card accent="neon" onClick={() => goTo('matches')}>
          <div className="flex items-center gap-2 mb-1">
            <IconBolt size={18} className="text-neon shrink-0" />
            <span className="h-display text-[11px] text-white/80 uppercase tracking-wider">Бліц</span>
          </div>
          <div className="h-display text-3xl text-neon glow-neon leading-none">
            {blitz ? fmtClock(blitz.start_at) : matches.data.blitz.schedule.map((s) => s.time)[0]}
          </div>
          <div className="text-muted text-[10px] mt-1">
            {blitz ? (blitz.registered ? 'ти в грі ✓' : 'реєстрація') : 'щодня'}
          </div>
        </Card>
      </div>

      <EnergyBarWithHint value={player.data.energy} max={energyMax} />

      <GiftCard quests={quests} />

      <DailyQuestsCard quests={quests} />

      <TournamentsCard leagues={matches.data.leagues} goTo={goTo} />

      {/* «Гравець» і «Трен-ня» прибрані — вони дублюють вкладки нижнього меню. */}
      <div className="grid grid-cols-2 gap-3">
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
            if (tg?.openTelegramLink) tg.openTelegramLink(CHAT_URL)
            else window.open(CHAT_URL, '_blank')
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
