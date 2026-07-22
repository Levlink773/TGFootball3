import { useState } from 'react'
import { getHallOfFame } from '../api'
import { useApi } from '../hooks'
import { Card, Loading, ErrorBox, Banner } from '../ui'
import { art } from '../assets/art'

const TABS = [
  { key: 'power', label: '💪 Сила' },
  { key: 'level', label: '📈 Рівень' },
  { key: 'mvp', label: '⭐ MVP' },
  { key: 'bombers', label: '⚽ Бомбардири' },
  { key: 'positions', label: '🧩 Позиції' },
]

const MEDALS = ['🥇', '🥈', '🥉']

function RatingTable({ block }) {
  if (!block || block.top.length === 0) {
    return <div className="text-muted text-center py-8 text-sm">Поки що порожньо</div>
  }
  return (
    <div>
      {block.top.map((row, i) => (
        <div key={`${row.user_id}-${i}`} className="flex items-center gap-3 py-2 border-t border-white/5 first:border-0">
          <span className="w-7 text-center">{MEDALS[i] || <span className="text-muted">{i + 1}</span>}</span>
          <span className="flex-1 h-display">{row.name}</span>
          <span className="text-muted text-xs">{row.position}</span>
          <span className="h-display text-gold glow-gold w-16 text-right">{row.value}</span>
        </div>
      ))}
      {block.me && (
        <div className="mt-3 pt-3 border-t border-neon/30 flex justify-between text-sm">
          <span className="text-neon">Твоє місце: #{block.me.place}</span>
          <span className="text-neon h-display">{block.me.value}</span>
        </div>
      )}
    </div>
  )
}

export default function HallOfFame() {
  const { data, error, loading, reload } = useApi(getHallOfFame)
  const [tab, setTab] = useState('power')
  const [position, setPosition] = useState(null)

  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  const positionKeys = Object.keys(data.positions)
  const activePosition = position || positionKeys[0]

  return (
    <div className="p-4 space-y-4">
      <Banner src={art['banner-halloffame']}>
        <span className="h-display text-2xl text-gold glow-gold">Зал Слави</span>
      </Banner>

      <div className="flex gap-2 overflow-x-auto pb-1">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`h-display whitespace-nowrap text-sm rounded-lg px-3 py-2 border ${
              tab === t.key
                ? 'text-gold border-gold/70 shadow-[0_0_12px_rgba(255,215,0,0.25)]'
                : 'text-muted border-white/10'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'positions' && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {positionKeys.map((key) => (
            <button
              key={key}
              onClick={() => setPosition(key)}
              className={`whitespace-nowrap text-xs rounded-full px-3 py-1.5 border ${
                activePosition === key ? 'text-neon border-neon/60' : 'text-muted border-white/10'
              }`}
            >
              {data.positions[key].label}
            </button>
          ))}
        </div>
      )}

      <Card>
        <RatingTable block={tab === 'positions' ? data.positions[activePosition] : data[tab]} />
      </Card>
    </div>
  )
}
