import { useState } from 'react'
import { getTeam, getJoinList, joinClub, leaveClub } from '../api'
import { useApi } from '../hooks'
import { Card, SectionTitle, Loading, ErrorBox, CtaButton, InitialsBadge } from '../ui'
import { art, clubCrest } from '../assets/art'

const MEDALS = ['🥇', '🥈', '🥉']

function openLink(url) {
  const tg = window.Telegram?.WebApp
  if (tg?.openTelegramLink && url.startsWith('https://t.me')) tg.openTelegramLink(url)
  else window.open(url, '_blank')
}

function JoinBrowser({ onJoined, setMessage }) {
  const { data, error, loading, reload } = useApi(getJoinList)
  const [busy, setBusy] = useState(null)
  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  const join = async (club) => {
    setBusy(club.id)
    try {
      const r = await joinClub(club.id)
      setMessage(`✅ Ти в команді «${r.club_name}»!`)
      onJoined()
    } catch (e) {
      setMessage(e.message)
    } finally {
      setBusy(null)
    }
  }

  if (!data.clubs.length) {
    return <div className="text-muted text-sm text-center py-4">Немає команд із вільними місцями</div>
  }
  return (
    <div className="space-y-2">
      {data.clubs.map((c) => (
        <Card key={c.id} className="flex items-center gap-3 py-3">
          <InitialsBadge name={c.name} src={clubCrest(c.name)} />
          <div className="flex-1 min-w-0">
            <div className="h-display text-base truncate">{c.name}</div>
            <div className="text-muted text-xs">
              {c.members_count}/{c.max_members} · Сила {c.total_power} · {c.league}
            </div>
          </div>
          {c.invite_only ? (
            <span className="text-muted text-xs">за запрошенням</span>
          ) : (
            <CtaButton disabled={busy === c.id} onClick={() => join(c)}>
              {busy === c.id ? '…' : 'Вступити'}
            </CtaButton>
          )}
        </Card>
      ))}
    </div>
  )
}

export default function Team({ goTo }) {
  const { data, error, loading, reload } = useApi(getTeam)
  const [message, setMessage] = useState(null)
  const [busy, setBusy] = useState(false)
  const [confirmLeave, setConfirmLeave] = useState(false)

  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  const leave = async () => {
    setBusy(true)
    try {
      await leaveClub()
      setMessage('Ти покинув команду')
      setConfirmLeave(false)
      reload()
    } catch (e) {
      setMessage(e.message)
    } finally {
      setBusy(false)
    }
  }

  const club = data.club

  return (
    <div className="p-4 space-y-4">
      <button onClick={() => goTo('home')} className="text-muted text-sm">‹ На головну</button>

      {message && (
        <div className="text-sm text-gold border border-gold/40 ring-glow-gold rounded-xl p-3" role="status">{message}</div>
      )}

      {!club ? (
        <>
          <div className="text-center">
            <div className="h-display text-3xl text-gold glow-gold">Команда</div>
            <div className="text-muted text-sm mt-1">Ти поки без команди — обери клуб і грай у лізі!</div>
          </div>
          <JoinBrowser onJoined={reload} setMessage={setMessage} />
        </>
      ) : (
        <>
          <Card accent="gold" className="relative overflow-hidden">
            <div className="flex items-center gap-3">
              <span className="w-14 h-14 rounded-full overflow-hidden border-2 border-gold ring-glow-gold shrink-0">
                <img src={clubCrest(club.name)} alt="" className="w-full h-full object-cover" />
              </span>
              <div className="flex-1 min-w-0">
                <div className="h-display text-2xl text-gold glow-gold truncate">{club.name}</div>
                <div className="text-muted text-xs uppercase">{club.league} · {club.stadium_name}</div>
              </div>
            </div>
            <div className="flex justify-between mt-3 text-center">
              <div>
                <div className="h-display text-2xl text-neon glow-neon">{club.total_power}</div>
                <div className="text-muted text-[10px] uppercase">Сила команди</div>
              </div>
              <div>
                <div className="h-display text-2xl text-white/90">{club.members_count}/{club.max_members}</div>
                <div className="text-muted text-[10px] uppercase">Гравців</div>
              </div>
              <div>
                <div className="h-display text-2xl text-gold">{club.is_owner ? 'Лідер' : 'Гравець'}</div>
                <div className="text-muted text-[10px] uppercase">Твоя роль</div>
              </div>
            </div>
            {club.description && <p className="text-white/70 text-xs mt-3">{club.description}</p>}
          </Card>

          <Card className="p-0 overflow-hidden">
            <div className="px-4 pt-3"><SectionTitle>Склад</SectionTitle></div>
            {club.members.map((m, i) => (
              <div
                key={m.user_id}
                className={`flex items-center gap-3 px-4 py-2 border-t border-white/5 ${m.is_me ? 'bg-neon/10' : ''}`}
              >
                <span className="w-7 text-center">{MEDALS[i] || <span className="text-muted">{i + 1}</span>}</span>
                <div className="flex-1 min-w-0">
                  <div className={`h-display text-sm truncate ${m.is_me ? 'text-neon' : ''}`}>{m.name}</div>
                  <div className="text-muted text-[11px]">{m.position} · {m.level} рів.</div>
                </div>
                <span className="h-display text-gold glow-gold">{m.full_power}</span>
              </div>
            ))}
          </Card>

          {data.infrastructure && (
            <Card>
              <div className="flex justify-between items-center mb-2">
                <SectionTitle accent="neon">Інфраструктура</SectionTitle>
                <span className="text-xs text-muted">{data.infrastructure.points} балів</span>
              </div>
              {data.infrastructure.objects.map((o) => (
                <div key={o.type} className="flex items-center justify-between py-1.5 border-t border-white/5 first:border-0">
                  <span className="text-sm">{o.label}</span>
                  <span className="text-xs text-muted">
                    рів. <b className="text-neon">{o.level}</b>/5
                    {o.bonus ? <span className="text-gold"> · {o.bonus > 0 ? '+' : ''}{o.bonus}%</span> : null}
                  </span>
                </div>
              ))}
              {club.is_owner && (
                <div className="text-muted text-[11px] mt-2">Покращення інфраструктури — поки в боті.</div>
              )}
            </Card>
          )}

          <div className="grid grid-cols-2 gap-3">
            {club.chat_url ? (
              <CtaButton onClick={() => openLink(club.chat_url)}>💬 Чат команди</CtaButton>
            ) : (
              <span />
            )}
            {!club.is_owner && (
              confirmLeave ? (
                <CtaButton color="gold" disabled={busy} onClick={leave}>
                  {busy ? '…' : 'Точно покинути?'}
                </CtaButton>
              ) : (
                <button
                  onClick={() => setConfirmLeave(true)}
                  className="text-red-400 text-sm border border-red-400/40 rounded-xl px-3 py-2"
                >
                  Покинути команду
                </button>
              )
            )}
          </div>
        </>
      )}

      {data.chat_url && (
        <button onClick={() => openLink(data.chat_url)} className="w-full text-neon text-sm border border-neon/40 rounded-xl px-3 py-2.5">
          🗣 Загальний чат гри
        </button>
      )}
    </div>
  )
}
