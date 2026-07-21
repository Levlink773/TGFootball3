import { useState } from 'react'
import { getLeagues, getPlayer } from '../api'
import { useApi } from '../hooks'
import { Card, Loading, ErrorBox, PillTabs, NextBar, InitialsBadge } from '../ui'
import { IconTrophy, IconStar, IconBall, IconShield } from '../icons'

const LEAGUE_ICONS = [IconTrophy, IconShield, IconStar, IconBall]

export default function League() {
  const { data, error, loading, reload } = useApi(getLeagues)
  const player = useApi(getPlayer)
  const [active, setActive] = useState(0)

  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  const league = data.leagues[active]
  const myClubId = player.data?.club?.id

  return (
    <div className="p-4 space-y-4">
      <PillTabs
        tabs={data.leagues.map((l, i) => {
          const Icon = LEAGUE_ICONS[i % LEAGUE_ICONS.length]
          // league names come with emoji prefixes from the bot — SVG icon replaces them
          return { key: l.type, label: l.name.replace(/^[^\p{L}]+/u, ''), icon: <Icon size={16} /> }
        })}
        active={active}
        onSelect={setActive}
      />

      <div className="flex justify-between items-center">
        <div>
          <div className="h-display text-2xl text-gold glow-gold leading-none">{league.name}</div>
          <span className="block w-10 h-0.5 bg-neon shadow-[0_0_8px_rgba(0,255,255,0.8)] mt-1.5" />
        </div>
        <span className={`h-display text-xs px-2.5 py-1 rounded-full border ${
          league.is_active ? 'text-neon border-neon/60 ring-glow-neon' : 'text-muted border-white/10'
        }`}>
          {league.is_active ? 'Триває зараз' : `${league.day_start}–${league.day_end} числа`}
        </span>
      </div>

      <Card className="p-0 overflow-hidden">
        {league.standings.length === 0 ? (
          <div className="text-muted text-center py-8 text-sm">Таблиця порожня — ліга ще не грала</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-muted text-[11px] uppercase tracking-wider">
                <th className="text-left py-2.5 pl-3 w-8">#</th>
                <th className="text-left py-2.5" colSpan={2}>Клуб</th>
                <th className="text-right py-2.5">Різниця</th>
                <th className="text-right py-2.5 pr-3">Очки</th>
              </tr>
            </thead>
            <tbody className="zebra">
              {league.standings.map((row, i) => {
                const mine = myClubId != null && row.club_id === myClubId
                return (
                  <tr
                    key={row.club_id}
                    className={`border-t border-white/5 ${
                      mine ? 'outline outline-1 -outline-offset-1 outline-neon bg-neon/10' : ''
                    }`}
                  >
                    <td className="py-2.5 pl-3 h-display text-lg text-white/80">{i + 1}</td>
                    <td className="py-1.5 w-11"><InitialsBadge name={row.club_name} active={mine} /></td>
                    <td className={`py-2.5 h-display text-base ${mine ? 'text-neon' : ''}`}>{row.club_name}</td>
                    <td className={`py-2.5 text-right h-display ${row.goal_difference >= 0 ? 'text-neon' : 'text-red-400'}`}>
                      {row.goal_difference >= 0 ? '+' : ''}{row.goal_difference}
                    </td>
                    <td className="py-2.5 pr-3 text-right h-display text-2xl text-gold glow-gold">{row.points}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </Card>

      <NextBar
        icon={<IconBall size={22} />}
        label="Наступний тур"
        time={`${String(league.match_hour).padStart(2, '0')}:00`}
      />
    </div>
  )
}
