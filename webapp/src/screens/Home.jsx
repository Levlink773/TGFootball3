import { getMatches, getPlayer } from '../api'
import { useApi } from '../hooks'
import { Card, Loading, ErrorBox } from '../ui'

function fmtTime(iso) {
  return new Date(iso).toLocaleString('uk-UA', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

export default function Home({ goTo }) {
  const player = useApi(getPlayer)
  const matches = useApi(getMatches)

  if (player.loading || matches.loading) return <Loading />
  if (player.error) return <ErrorBox error={player.error} onRetry={player.reload} />
  if (matches.error) return <ErrorBox error={matches.error} onRetry={matches.reload} />

  const nextMatch = matches.data.leagues.map((l) => l.next_match).find(Boolean)
  const blitz = matches.data.blitz.next

  return (
    <div className="p-4 space-y-4">
      <div className="text-center py-3">
        <div className="h-display text-3xl text-gold glow-gold">TG FOOTBALL</div>
        <div className="text-muted text-sm mt-1">
          Привіт, {player.data.name}! ⚡ {player.data.energy} · 💰 {player.data.money}
        </div>
      </div>

      <Card accent="gold" className="cursor-pointer" onClick={() => goTo('matches')}>
        <div onClick={() => goTo('matches')}>
          <div className="h-display text-lg text-gold mb-1">⚽ Наступний матч</div>
          {nextMatch ? (
            <div className="flex justify-between items-center">
              <span>vs {nextMatch.opponent_club_name || '—'}</span>
              <span className="text-neon h-display">{fmtTime(nextMatch.time_to_start)}</span>
            </div>
          ) : (
            <div className="text-muted text-sm">Немає запланованих матчів — зазирни у вкладку Матчі</div>
          )}
        </div>
      </Card>

      <Card accent="neon">
        <div onClick={() => goTo('matches')}>
          <div className="h-display text-lg text-neon mb-1">⚡ Бліц</div>
          {blitz ? (
            <div className="flex justify-between items-center">
              <span className="text-sm">
                {blitz.registered ? '✅ Ти зареєстрований' : 'Реєстрація відкрита'}
              </span>
              <span className="h-display text-neon glow-neon">{fmtTime(blitz.start_at)}</span>
            </div>
          ) : (
            <div className="text-muted text-sm">Щодня о {matches.data.blitz.schedule.map((s) => s.time).join(' та ')}</div>
          )}
        </div>
      </Card>

      <div className="grid grid-cols-2 gap-3">
        <Card className="text-center" >
          <button className="w-full" onClick={() => goTo('player')}>
            <div className="text-2xl mb-1">🏃</div>
            <div className="h-display text-sm">Гравець</div>
          </button>
        </Card>
        <Card className="text-center">
          <button className="w-full" onClick={() => goTo('training')}>
            <div className="text-2xl mb-1">🏋️</div>
            <div className="h-display text-sm">Тренування</div>
          </button>
        </Card>
      </div>
    </div>
  )
}
