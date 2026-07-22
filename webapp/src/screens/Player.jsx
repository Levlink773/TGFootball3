import { getPlayer } from '../api'
import { useApi } from '../hooks'
import { Card, Loading, ErrorBox, StatBar, EnergyBar, InitialsBadge } from '../ui'
import { IconBoot, IconTarget, IconShield, IconRun, IconHeart } from '../icons'
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

export default function Player() {
  const { data, error, loading, reload } = useApi(getPlayer)
  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  const [firstName, ...rest] = (data.name || '').split(' ')
  const energyMax = data.vip_active ? ENERGY_MAX_VIP : ENERGY_MAX

  return (
    <div className="p-4 space-y-4">
      {/* Hero card — frame 1 */}
      <Card accent="gold" className="relative overflow-hidden">
        {avatarArt(data.gender, data.position) && (
          <img
            src={avatarArt(data.gender, data.position)}
            alt=""
            className="absolute right-0 top-0 h-full w-1/2 object-cover object-top pointer-events-none opacity-90 [mask-image:linear-gradient(to_left,black_55%,transparent)]"
          />
        )}
        <div
          className="absolute inset-0 pointer-events-none opacity-60"
          style={{ background: 'radial-gradient(120% 90% at 80% 0%, rgba(0,255,255,0.08) 0%, transparent 55%), radial-gradient(120% 90% at 0% 100%, rgba(255,215,0,0.10) 0%, transparent 55%)' }}
        />
        <div className="relative flex justify-between min-h-[150px]">
          <div>
            {rest.length > 0 ? (
              <>
                <div className="h-display text-3xl leading-none text-white">{firstName}</div>
                <div className="h-display text-4xl leading-tight text-gold glow-gold">{rest.join(' ')}</div>
              </>
            ) : (
              <div className="h-display text-4xl leading-tight text-gold glow-gold">{firstName}</div>
            )}
            {data.vip_active && (
              <span className="inline-block mt-2 h-display text-xs text-gold border border-gold/60 rounded-full px-2 py-0.5">
                ★ VIP
              </span>
            )}
          </div>
          <div className="flex flex-col items-end gap-2">
            <span
              className="w-14 h-14 rounded-full border-2 border-neon ring-glow-neon flex items-center justify-center h-display text-xl text-neon"
              title={data.position}
            >
              {POSITION_SHORT[data.position] || data.position}
            </span>
            {data.level != null && (
              <span className="h-display text-sm text-neon border border-neon/50 rounded-lg px-2 py-0.5">
                {data.level} рів.
              </span>
            )}
          </div>
        </div>
        <div className="relative flex items-end justify-end gap-3 mt-2">
          <span className="h-display text-sm text-white/80 mb-2">Сила</span>
          <span className="h-display text-6xl leading-none text-gold glow-gold">
            {Math.round(data.full_power)}
          </span>
        </div>
      </Card>

      {/* Stats — gold icon · label · cyan bar · value */}
      <Card>
        {(() => {
          const statMax = Math.max(100, ...Object.values(data.stats))
          return STATS.map(({ key, label, Icon }) => (
            <StatBar key={key} label={label} value={data.stats[key]} max={statMax} icon={<Icon size={20} />} />
          ))
        })()}
      </Card>

      <EnergyBar value={data.energy} max={energyMax} />

      {data.club && (
        <Card>
          <div className="flex items-center gap-3">
            <InitialsBadge name={data.club.name} src={clubCrest(data.club.name)} />
            <div className="flex-1">
              <div className="h-display text-lg">{data.club.name}</div>
              <div className="text-muted text-xs uppercase">{data.club.league}</div>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
