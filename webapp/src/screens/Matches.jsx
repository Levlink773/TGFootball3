import { useState } from 'react'
import { getMatches, registerMatch, registerBlitz } from '../api'
import { useApi } from '../hooks'
import { Card, Loading, ErrorBox, CtaButton } from '../ui'
import { IconBolt, IconTrophy } from '../icons'

function fmtTime(iso) {
  const d = new Date(iso)
  return d.toLocaleString('uk-UA', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function fmtClock(iso) {
  return new Date(iso).toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
}

function RegisterButton({ registered, busy, onClick, disabled, color }) {
  if (registered) {
    return <span className="h-display text-neon glow-neon text-sm whitespace-nowrap">✓ У грі</span>
  }
  return (
    <CtaButton onClick={onClick} disabled={busy || disabled} color={color}>
      {busy ? '…' : 'Реєстрація'}
    </CtaButton>
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
        <div className="text-sm text-gold border border-gold/40 ring-glow-gold rounded-xl p-3">{message}</div>
      )}

      {/* Blitz — cyan hero card */}
      <Card accent="neon">
        <div className="flex items-center gap-2 mb-2">
          <IconBolt size={22} className="text-gold" />
          <span className="h-display text-xl text-neon glow-neon">Бліц-турніри</span>
        </div>
        <div className="text-muted text-sm mb-3">
          Щодня: {data.blitz.schedule.map((s) => s.time).join(' та ')}
        </div>
        {data.blitz.next ? (
          <div className="flex items-center justify-between gap-3">
            <div>
              <div className="h-display text-4xl text-neon glow-neon leading-none">
                {fmtClock(data.blitz.next.start_at)}
              </div>
              <div className="text-muted text-xs mt-1">
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
            <div className="flex items-center gap-2">
              <IconTrophy size={18} className="text-gold" />
              <span className="h-display text-lg text-gold">{league.name}</span>
            </div>
            <span className={`h-display text-xs px-2.5 py-1 rounded-full border ${
              league.is_active ? 'text-neon border-neon/60' : 'text-muted border-white/10'
            }`}>
              {league.is_active ? 'Активна' : `${league.day_start}–${league.day_end} числа`}
            </span>
          </div>
          {league.next_match ? (
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="h-display text-base">
                  vs {league.next_match.opponent_club_name || '—'}
                </div>
                <div className="text-neon text-xs h-display mt-0.5">{fmtTime(league.next_match.time_to_start)}</div>
              </div>
              <RegisterButton
                color="gold"
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
