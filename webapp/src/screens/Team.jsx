import { useState } from 'react'
import {
  getTeam, getJoinList, joinClub, leaveClub,
  kickMember, transferOwner, renameClub, setInviteOnly, setClubDescription, upgradeInfrastructure,
} from '../api'
import { useApi } from '../hooks'
import { Card, SectionTitle, Loading, ErrorBox, CtaButton, InitialsBadge } from '../ui'
import { clubCrest } from '../assets/art'

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

// Bottom sheet with owner actions for one member: transfer leadership / kick.
function MemberSheet({ member, busy, onTransfer, onKick, onClose }) {
  const [confirm, setConfirm] = useState(null) // 'transfer' | 'kick'
  return (
    <div className="fixed inset-0 z-30 flex items-end" onClick={onClose}>
      <div className="absolute inset-0 bg-black/70" />
      <div
        className="relative w-full max-w-[422px] mx-auto bg-card border-t border-gold/40 rounded-t-2xl p-4 space-y-3"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="h-display text-xl text-white">{member.name}</div>
        <div className="text-muted text-xs">{member.position} · {member.level} рів. · сила {member.full_power}</div>
        {confirm === 'transfer' ? (
          <CtaButton color="gold" className="w-full" disabled={busy} onClick={onTransfer}>
            {busy ? '…' : 'Точно передати лідерство?'}
          </CtaButton>
        ) : (
          <button
            onClick={() => setConfirm('transfer')}
            className="w-full h-display text-sm rounded-xl px-4 py-2.5 border border-gold/50 text-gold"
          >
            👑 Передати лідерство
          </button>
        )}
        {confirm === 'kick' ? (
          <button
            disabled={busy}
            onClick={onKick}
            className="w-full h-display text-sm rounded-xl px-4 py-2.5 border border-red-400/60 text-red-300 disabled:opacity-50"
          >
            {busy ? '…' : 'Точно вигнати?'}
          </button>
        ) : (
          <button
            onClick={() => setConfirm('kick')}
            className="w-full h-display text-sm rounded-xl px-4 py-2.5 border border-red-400/40 text-red-300"
          >
            ⛔ Вигнати з команди
          </button>
        )}
      </div>
    </div>
  )
}

// Owner-only settings: rename, description, invite-only.
function OwnerSettings({ club, busy, run }) {
  const [name, setName] = useState(club.name)
  const [desc, setDesc] = useState(club.description === 'Не вказано' ? '' : club.description || '')
  return (
    <Card>
      <SectionTitle accent="neon">Керування командою</SectionTitle>
      <label className="text-muted text-xs">Назва команди</label>
      <div className="flex gap-2 mt-1 mb-3">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={30}
          className="flex-1 bg-card2 rounded-lg px-3 py-2 text-sm border border-white/10 focus:border-neon outline-none"
        />
        <CtaButton disabled={busy || name.trim() === club.name} onClick={() => run(() => renameClub(name.trim()))}>
          Зберегти
        </CtaButton>
      </div>
      <label className="text-muted text-xs">Опис</label>
      <div className="flex gap-2 mt-1 mb-3">
        <input
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
          maxLength={255}
          placeholder="Розкажи про команду…"
          className="flex-1 bg-card2 rounded-lg px-3 py-2 text-sm border border-white/10 focus:border-neon outline-none"
        />
        <CtaButton disabled={busy} onClick={() => run(() => setClubDescription(desc.trim()))}>
          Зберегти
        </CtaButton>
      </div>
      <div className="flex items-center justify-between border-t border-white/5 pt-3">
        <div>
          <div className="text-sm">Тільки за запрошенням</div>
          <div className="text-muted text-[11px]">Новачки подають заявку в боті</div>
        </div>
        <button
          disabled={busy}
          onClick={() => run(() => setInviteOnly(!club.invite_only))}
          className={`w-12 h-7 rounded-full transition-colors relative ${club.invite_only ? 'bg-neon' : 'bg-card2 border border-white/15'}`}
        >
          <span className={`absolute top-0.5 w-6 h-6 rounded-full bg-white transition-all ${club.invite_only ? 'left-[22px]' : 'left-0.5'}`} />
        </button>
      </div>
    </Card>
  )
}

// One infrastructure building: level, bonus, upgrade button (owner), level table.
function InfraRow({ obj, points, isOwner, busy, onUpgrade }) {
  const [open, setOpen] = useState(false)
  const maxed = obj.level >= 5
  const affordable = obj.next_cost != null && points >= obj.next_cost
  return (
    <div className="border-t border-white/5 first:border-0 py-2">
      <div className="flex items-center justify-between">
        <button onClick={() => setOpen((v) => !v)} className="text-left flex-1">
          <div className="text-sm">{obj.label}</div>
          <div className="text-muted text-[11px]">
            рів. <b className="text-neon">{obj.level}</b>/5
            {obj.bonus ? <span className="text-gold"> · {obj.bonus > 0 ? '+' : ''}{obj.bonus}%</span> : null}
            <span className="text-neon/60"> · деталі {open ? '▲' : '▼'}</span>
          </div>
        </button>
        {isOwner && !maxed && (
          <CtaButton
            color="gold"
            disabled={busy || !affordable}
            onClick={() => onUpgrade(obj.type)}
          >
            {affordable ? `Покращити · ${obj.next_cost}` : `Треба ${obj.next_cost}`}
          </CtaButton>
        )}
        {maxed && <span className="text-gold text-xs h-display">MAX</span>}
      </div>
      {open && (
        <div className="mt-2 rounded-lg bg-card2 p-2 space-y-1">
          {obj.levels.map((l) => (
            <div key={l.level} className={`flex justify-between text-[11px] ${l.level === obj.level ? 'text-neon' : 'text-muted'}`}>
              <span>Рів. {l.level}{l.level === obj.level ? ' (зараз)' : ''}</span>
              <span>{l.bonus > 0 ? '+' : ''}{l.bonus}%{l.cost ? ` · ${l.cost} балів` : ''}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function Team({ goTo }) {
  const { data, error, loading, reload } = useApi(getTeam)
  const [message, setMessage] = useState(null)
  const [busy, setBusy] = useState(false)
  const [confirmLeave, setConfirmLeave] = useState(false)
  const [sheetMember, setSheetMember] = useState(null)

  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  const club = data.club

  // shared runner for owner actions: run fn, surface message, reload
  const run = async (fn, okMsg) => {
    setBusy(true)
    setMessage(null)
    try {
      await fn()
      if (okMsg) setMessage(okMsg)
      setSheetMember(null)
      reload()
    } catch (e) {
      setMessage(e.message)
    } finally {
      setBusy(false)
    }
  }

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
            {club.description && club.description !== 'Не вказано' && (
              <p className="text-white/70 text-xs mt-3">{club.description}</p>
            )}
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
                {club.is_owner && !m.is_me && (
                  <button
                    onClick={() => setSheetMember(m)}
                    className="text-muted hover:text-neon text-lg px-1"
                    aria-label="Дії з гравцем"
                  >
                    ⚙
                  </button>
                )}
              </div>
            ))}
          </Card>

          {club.is_owner && <OwnerSettings club={club} busy={busy} run={run} />}

          {data.infrastructure && (
            <Card>
              <div className="flex justify-between items-center mb-1">
                <SectionTitle accent="neon">Інфраструктура</SectionTitle>
                <span className="text-xs text-gold h-display">{data.infrastructure.points} балів</span>
              </div>
              {!club.is_owner && (
                <div className="text-muted text-[11px] mb-1">Покращення доступні лідеру команди.</div>
              )}
              {data.infrastructure.objects.map((o) => (
                <InfraRow
                  key={o.type}
                  obj={o}
                  points={data.infrastructure.points}
                  isOwner={club.is_owner}
                  busy={busy}
                  onUpgrade={(type) => run(() => upgradeInfrastructure(type), 'Об’єкт покращено!')}
                />
              ))}
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

      {sheetMember && (
        <MemberSheet
          member={sheetMember}
          busy={busy}
          onTransfer={() => run(() => transferOwner(sheetMember.user_id), 'Лідерство передано')}
          onKick={() => run(() => kickMember(sheetMember.user_id), 'Гравця виключено')}
          onClose={() => setSheetMember(null)}
        />
      )}
    </div>
  )
}
