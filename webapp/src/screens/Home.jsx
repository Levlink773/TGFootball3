import { getMatches, getPlayer, getTeam } from '../api'
import { useApi } from '../hooks'
import { Card, Loading, ErrorBox, StatBar, EnergyBar, CtaButton } from '../ui'
import { IconBoot, IconTarget, IconShield, IconRun, IconHeart, IconCalendar } from '../icons'
import { avatarArt, clubCrest } from '../assets/art'

const STATS = [
  { key: 'technique', label: 'Техніка', Icon: IconBoot },
  { key: 'kicks', label: 'Удари', Icon: IconTarget },
  { key: 'ball_selection', label: 'Відбір', Icon: IconShield },
  { key: 'speed', label: 'Швидкість', Icon: IconRun },
  { key: 'endurance', label: 'Витривалість', Icon: IconHeart },
]

const ENERGY_MAX_VIP = 300
const ENERGY_MAX = 150

const POSITION_SHORT = {
  'Нападник': 'НП',
  'Півзахисник': 'ПЗ',
  'Захисник': 'ЗХ',
  'Воротар': 'ВР',
}

function fmtClock(iso) {
  return new Date(iso).toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
}

// Головна = профіль гравця, 1:1 за ескізом v1-neon frame 1:
// hero card → stat bars → energy → club → next match.
export default function Home({ goTo }) {
  const player = useApi(getPlayer)
  const team = useApi(getTeam)
  const matches = useApi(getMatches)

  if (player.loading || matches.loading || team.loading) return <Loading />
  if (player.error) return <ErrorBox error={player.error} onRetry={player.reload} />
  if (matches.error) return <ErrorBox error={matches.error} onRetry={matches.reload} />

  const data = player.data
  const [firstName, ...rest] = (data.name || '').split(' ')
  const energyMax = data.vip_active ? ENERGY_MAX_VIP : ENERGY_MAX
  const nextMatch = matches.data.leagues.map((l) => l.next_match).find(Boolean)
  const club = team.error ? null : team.data?.club

  return (
    <div className="p-4 space-y-4">
      {/* Hero card */}
      <Card accent="gold" className="relative overflow-hidden hero-streaks">
        {avatarArt(data.gender, data.position) && (
          <img
            src={avatarArt(data.gender, data.position)}
            alt=""
            className="absolute right-6 top-0 h-full w-3/5 object-cover object-top pointer-events-none [mask-image:linear-gradient(to_left,transparent_0%,black_25%,black_75%,transparent_100%)]"
          />
        )}
        <div className="relative flex justify-between min-h-[170px]">
          <div>
            <div className="h-display text-3xl leading-none text-white break-words max-w-[200px]">{firstName}</div>
            {rest.length > 0 && (
              <div className="h-display text-[44px] leading-[1.05] text-gold glow-gold break-words max-w-[210px] tracking-tight">{rest.join(' ')}</div>
            )}
            {data.vip_active && (
              <span className="inline-block mt-2 h-display text-xs text-gold border border-gold/60 rounded-full px-2 py-0.5">
                ★ VIP
              </span>
            )}
          </div>
          <div className="flex flex-col items-end gap-2">
            <span
              className="w-14 h-14 rounded-full border-2 border-neon ring-glow-neon bg-pitch/60 flex items-center justify-center h-display text-xl text-neon"
              title={data.position}
            >
              {POSITION_SHORT[data.position] || data.position}
            </span>
            {data.level != null && (
              <span className="h-display text-sm text-neon border border-neon/50 bg-pitch/60 rounded-lg px-2 py-0.5">
                {data.level} рів.
              </span>
            )}
          </div>
        </div>
        <div className="relative flex items-end justify-end gap-3 mt-1">
          <span className="h-display text-base text-white/85 mb-2.5">Сила</span>
          <span className="h-display text-7xl leading-none text-gold glow-gold">
            {Math.round(data.full_power)}
          </span>
        </div>
      </Card>

      {/* Stat bars */}
      <Card>
        {(() => {
          const statMax = Math.max(100, ...Object.values(data.stats))
          return STATS.map(({ key, label, Icon }) => (
            <StatBar key={key} label={label} value={data.stats[key]} max={statMax} icon={<Icon size={20} />} />
          ))
        })()}
      </Card>

      <EnergyBar value={data.energy} max={energyMax} />

      {/* Club */}
      <Card className="cursor-pointer" onClick={() => goTo?.('team')}>
        {club ? (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span className="w-14 h-14 rounded-full border border-white/15 bg-card2 overflow-hidden shrink-0 flex items-center justify-center">
                {clubCrest(club.name) ? (
                  <img src={clubCrest(club.name)} alt="" className="w-full h-full object-cover" />
                ) : (
                  <span className="h-display text-lg">{(club.name || '?')[0]}</span>
                )}
              </span>
              <div className="min-w-0">
                <div className="h-display text-xl leading-tight truncate">{club.name}</div>
                <div className="text-muted text-[11px] uppercase tracking-wider">Сила команди</div>
                <div className="h-display text-xl text-gold glow-gold leading-none">
                  {Math.round(club.total_power).toLocaleString('uk-UA')}
                </div>
              </div>
            </div>
            {club.members?.length > 0 && (
              <div className="flex gap-1.5 overflow-x-auto pb-1 -mx-1 px-1">
                {club.members.map((m) => (
                  <span
                    key={m.user_id}
                    title={m.name}
                    className={`w-9 h-9 rounded-full shrink-0 overflow-hidden border ${
                      m.is_me ? 'border-gold ring-glow-gold' : 'border-neon/70'
                    } bg-card2 flex items-center justify-center`}
                  >
                    {avatarArt(m.gender, m.position) ? (
                      <img src={avatarArt(m.gender, m.position)} alt="" className="w-full h-full object-cover object-top" />
                    ) : (
                      <span className="h-display text-xs text-white/80">{(m.name || '?')[0]}</span>
                    )}
                  </span>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <span className="text-muted text-sm">Ти без команди</span>
            <span className="text-neon text-sm h-display">Знайти команду ›</span>
          </div>
        )}
      </Card>

      {/* Next match */}
      <Card accent="gold">
        <div className="flex items-center gap-3">
          <IconCalendar size={30} className="text-gold shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="h-display text-sm text-white/85 leading-none">Наступний матч</div>
            {nextMatch ? (
              <div className="h-display text-4xl text-gold glow-gold leading-tight">
                {fmtClock(nextMatch.time_to_start)}
              </div>
            ) : (
              <div className="text-muted text-xs mt-1.5">Немає запланованих матчів</div>
            )}
          </div>
          <CtaButton onClick={() => goTo('matches')}>
            {nextMatch ? 'Готуватися до матчу ›' : 'До матчів ›'}
          </CtaButton>
        </div>
      </Card>
    </div>
  )
}
