import { getMatches, getPlayer } from '../api'
import { useApi } from '../hooks'
import { Card, Loading, ErrorBox, NextBar, CtaButton, EnergyBar } from '../ui'
import { IconCalendar, IconBolt, IconUser, IconDumbbell, IconChat } from '../icons'
import { art } from '../assets/art'

// game community chat, same link the bot sends to new members
const CHAT_URL = import.meta.env.VITE_GAME_CHAT_URL || 'https://t.me/tgfootballchat'

function fmtTime(iso) {
  return new Date(iso).toLocaleString('uk-UA', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function fmtClock(iso) {
  return new Date(iso).toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
}

export default function Home({ goTo }) {
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

      <div className="grid grid-cols-3 gap-3">
        <Card className="text-center py-3 cursor-pointer" onClick={() => goTo('player')}>
          <IconUser size={24} className="text-neon mx-auto mb-1" />
          <div className="h-display text-sm">Гравець</div>
        </Card>
        <Card className="text-center py-3 cursor-pointer" onClick={() => goTo('training')}>
          <IconDumbbell size={24} className="text-neon mx-auto mb-1" />
          <div className="h-display text-sm">Трен-ня</div>
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
