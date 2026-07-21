import { getPlayer } from '../api'
import { useApi } from '../hooks'
import { Card, SectionTitle, Loading, ErrorBox, StatBar } from '../ui'

const STAT_LABELS = {
  technique: 'Техніка',
  kicks: 'Удари',
  ball_selection: 'Відбір',
  speed: 'Швидкість',
  endurance: 'Витривалість',
}

export default function Player() {
  const { data, error, loading, reload } = useApi(getPlayer)
  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  return (
    <div className="p-4 space-y-4">
      <Card accent="gold">
        <div className="flex items-center justify-between">
          <div>
            <div className="h-display text-2xl text-gold glow-gold">{data.name}</div>
            <div className="text-muted text-sm">{data.position} · {data.club?.name || 'Без клубу'}</div>
          </div>
          <div className="text-right">
            <div className="h-display text-3xl text-neon glow-neon">{data.full_power.toFixed(1)}</div>
            <div className="text-muted text-xs uppercase">Сила</div>
          </div>
        </div>
        {data.vip_active && (
          <div className="mt-2 inline-block text-xs text-gold border border-gold/50 rounded-full px-2 py-0.5">
            ⭐ VIP активний
          </div>
        )}
      </Card>

      <div className="grid grid-cols-2 gap-3">
        <Card>
          <div className="text-muted text-xs uppercase mb-1">⚡ Енергія</div>
          <div className="h-display text-2xl text-neon">{data.energy}</div>
        </Card>
        <Card>
          <div className="text-muted text-xs uppercase mb-1">💰 Монети</div>
          <div className="h-display text-2xl text-gold">{data.money}</div>
        </Card>
      </div>

      <Card>
        <SectionTitle>Характеристики</SectionTitle>
        {Object.entries(data.stats).map(([key, value]) => (
          <StatBar key={key} label={STAT_LABELS[key] || key} value={value} />
        ))}
      </Card>

      {data.club && (
        <Card>
          <SectionTitle accent="neon">Клуб</SectionTitle>
          <div className="flex justify-between">
            <span>{data.club.name}</span>
            <span className="text-muted">{data.club.league}</span>
          </div>
        </Card>
      )}
    </div>
  )
}
