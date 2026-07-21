import { useState } from 'react'
import { getMatches, registerMatch, registerBlitz } from '../api'
import { useApi } from '../hooks'
import { Card, SectionTitle, Loading, ErrorBox } from '../ui'

function fmtTime(iso) {
  const d = new Date(iso)
  return d.toLocaleString('uk-UA', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function RegisterButton({ registered, busy, onClick, disabled }) {
  if (registered) {
    return <span className="text-neon text-sm">✅ Зареєстрований</span>
  }
  return (
    <button
      onClick={onClick}
      disabled={busy || disabled}
      className="h-display text-sm bg-gold text-black rounded-lg px-4 py-2 disabled:opacity-40"
    >
      {busy ? '…' : 'Реєстрація'}
    </button>
  )
}

export default function Matches() {
  const { data, error, loading, reload } = useApi(getMatches)
  const [busy, setBusy] = useState(null)
  const [message, setMessage] = useState(null)

  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  const act = async (key, fn) => {
    setBusy(key)
    setMessage(null)
    try {
      await fn()
      reload()
    } catch (e) {
      setMessage(e.message)
    } finally {
      setBusy(null)
    }
  }

  return (
    <div className="p-4 space-y-4">
      {message && (
        <div className="text-sm text-gold border border-gold/40 rounded-lg p-3">{message}</div>
      )}

      <Card accent="neon">
        <SectionTitle accent="neon">⚡ Бліц-турніри</SectionTitle>
        <div className="text-muted text-sm mb-2">
          Щодня: {data.blitz.schedule.map((s) => s.time).join(' та ')}
        </div>
        {data.blitz.next ? (
          <div className="flex items-center justify-between">
            <div>
              <div className="h-display text-xl text-neon glow-neon">
                {fmtTime(data.blitz.next.start_at)}
              </div>
              <div className="text-muted text-xs">
                Гравців: {data.blitz.next.participants}/{data.blitz.next.max_players}
              </div>
            </div>
            <RegisterButton
              registered={data.blitz.next.registered}
              busy={busy === 'blitz'}
              disabled={!data.blitz.next.can_register}
              onClick={() => act('blitz', registerBlitz)}
            />
          </div>
        ) : (
          <div className="text-muted">Наступний бліц ще не заплановано</div>
        )}
      </Card>

      {data.leagues.map((league) => (
        <Card key={league.type}>
          <div className="flex justify-between items-center mb-2">
            <div className="h-display text-lg text-gold">{league.name}</div>
            <span className={`text-xs px-2 py-0.5 rounded-full border ${
              league.is_active ? 'text-neon border-neon/50' : 'text-muted border-white/10'
            }`}>
              {league.is_active ? 'Активна' : `${league.day_start}–${league.day_end} числа`}
            </span>
          </div>
          {league.next_match ? (
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm">
                  vs <span className="font-semibold">{league.next_match.opponent_club_name || '—'}</span>
                </div>
                <div className="text-muted text-xs">{fmtTime(league.next_match.time_to_start)}</div>
              </div>
              <RegisterButton
                registered={league.next_match.registered}
                busy={busy === league.type}
                onClick={() => act(league.type, () => registerMatch(league.next_match.match_id))}
              />
            </div>
          ) : (
            <div className="text-muted text-sm">
              {league.is_active ? 'Немає запланованих матчів' : 'Ліга ще не почалася'}
            </div>
          )}
        </Card>
      ))}
    </div>
  )
}
