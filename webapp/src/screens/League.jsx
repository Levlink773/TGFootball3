import { useState } from 'react'
import { getLeagues } from '../api'
import { useApi } from '../hooks'
import { Card, Loading, ErrorBox } from '../ui'

export default function League() {
  const { data, error, loading, reload } = useApi(getLeagues)
  const [active, setActive] = useState(0)

  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  const league = data.leagues[active]

  return (
    <div className="p-4 space-y-4">
      <div className="flex gap-2 overflow-x-auto pb-1">
        {data.leagues.map((l, i) => (
          <button
            key={l.type}
            onClick={() => setActive(i)}
            className={`h-display whitespace-nowrap text-sm rounded-lg px-3 py-2 border ${
              i === active
                ? 'text-gold border-gold/70 shadow-[0_0_12px_rgba(255,215,0,0.25)]'
                : 'text-muted border-white/10'
            }`}
          >
            {l.name}
          </button>
        ))}
      </div>

      <div className="flex justify-between items-center">
        <span className={`text-xs px-2 py-0.5 rounded-full border ${
          league.is_active ? 'text-neon border-neon/50' : 'text-muted border-white/10'
        }`}>
          {league.is_active ? 'Триває зараз' : `Іде ${league.day_start}–${league.day_end} числа`}
        </span>
        <span className="text-muted text-xs">Матчі о {league.match_hour}:00</span>
      </div>

      <Card className="p-0 overflow-hidden">
        {league.standings.length === 0 ? (
          <div className="text-muted text-center py-8 text-sm">Таблиця порожня — ліга ще не грала</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-muted text-xs uppercase">
                <th className="text-left py-2 pl-3 w-8">#</th>
                <th className="text-left py-2">Клуб</th>
                <th className="text-right py-2">РГ</th>
                <th className="text-right py-2 pr-3">Очки</th>
              </tr>
            </thead>
            <tbody>
              {league.standings.map((row, i) => (
                <tr key={row.club_id} className="border-t border-white/5">
                  <td className="py-2.5 pl-3 text-muted">{i + 1}</td>
                  <td className="py-2.5 h-display">{row.club_name}</td>
                  <td className={`py-2.5 text-right ${row.goal_difference >= 0 ? 'text-neon' : 'text-red-400'}`}>
                    {row.goal_difference >= 0 ? '+' : ''}{row.goal_difference}
                  </td>
                  <td className="py-2.5 pr-3 text-right h-display text-lg text-gold glow-gold">{row.points}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  )
}
