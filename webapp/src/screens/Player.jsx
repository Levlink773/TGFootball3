import { useState } from 'react'
import { getMatches, getPlayer, getTeam, getInventory, equipItem, unequipItem, sellItem } from '../api'
import { useApi } from '../hooks'
import { Card, Loading, ErrorBox, StatBar, EnergyBar, CtaButton } from '../ui'
import { IconBoot, IconTarget, IconShield, IconRun, IconHeart, IconCalendar, IconShirt } from '../icons'
import { avatarArt, clubCrest, gearArt } from '../assets/art'

const STATS = [
  { key: 'technique', label: 'Техніка', Icon: IconBoot },
  { key: 'kicks', label: 'Удари', Icon: IconTarget },
  { key: 'ball_selection', label: 'Відбір', Icon: IconShield },
  { key: 'speed', label: 'Швидкість', Icon: IconRun },
  { key: 'endurance', label: 'Витривалість', Icon: IconHeart },
]

const SLOTS = [
  { category: 'T_SHIRT', field: 't_shirt_id', label: 'Футболка' },
  { category: 'SHORTS', field: 'shorts_id', label: 'Шорти' },
  { category: 'GAITERS', field: 'gaiters_id', label: 'Гетри' },
  { category: 'BOOTS', field: 'boots_id', label: 'Бутси' },
]

const STAT_SHORT = {
  technique: 'ТЕХ', kicks: 'УДР', ball_selection: 'ВДБ', speed: 'ШВД', endurance: 'ВТР',
}

const ENERGY_MAX_VIP = 300
const ENERGY_MAX = 150

const POSITION_SHORT = {
  'Нападник': 'НП',
  'Півзахисник': 'ПЗ',
  'Захисник': 'ЗХ',
  'Воротар': 'ВР',
}

function fmtClock(iso) {
  return new Date(iso).toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
}

// Bottom sheet for one owned item: stats + Одягнути/Зняти/Продати.
function ItemSheet({ item, isEquipped, busy, onEquip, onUnequip, onSell, onClose }) {
  return (
    <div className="fixed inset-0 z-30 flex items-end" onClick={onClose}>
      <div className="absolute inset-0 bg-black/70" />
      <div
        className="relative w-full max-w-[422px] mx-auto bg-card border-t border-gold/40 rounded-t-2xl p-4 space-y-3"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3">
          {gearArt(item.name) && (
            <img src={gearArt(item.name)} alt="" className="w-12 h-12 object-contain rounded-lg bg-card2 shrink-0" />
          )}
          <div className="h-display text-xl text-white flex-1">{item.name}</div>
          {isEquipped && (
            <span className="h-display text-xs text-gold border border-gold/60 rounded-full px-2 py-0.5 shrink-0">одягнуто</span>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          {Object.entries(item.stats || {}).filter(([, v]) => v).map(([k, v]) => (
            <span key={k} className="h-display text-xs text-neon border border-neon/40 rounded-lg px-2 py-1">
              {STAT_SHORT[k] || k} +{v}
            </span>
          ))}
        </div>
        <div className="flex gap-2 pt-1">
          {isEquipped ? (
            <CtaButton disabled={busy} onClick={onUnequip} className="flex-1">Зняти</CtaButton>
          ) : (
            <CtaButton disabled={busy} onClick={onEquip} className="flex-1">Одягнути</CtaButton>
          )}
          <button
            disabled={busy}
            onClick={onSell}
            className="flex-1 h-display text-sm rounded-xl px-4 py-2.5 border border-red-400/60 text-red-300 disabled:opacity-50"
          >
            Продати · {item.sell_price} 🪙
          </button>
        </div>
      </div>
    </div>
  )
}

// Гравець — профіль: hero card → stat bars → energy → екіпірування → club → next match.
export default function Player({ goTo }) {
  const player = useApi(getPlayer)
  const team = useApi(getTeam)
  const matches = useApi(getMatches)
  const inventory = useApi(getInventory)
  const [openItem, setOpenItem] = useState(null) // item object from inventory
  const [busy, setBusy] = useState(false)

  if (player.loading || matches.loading || team.loading) return <Loading />
  if (player.error) return <ErrorBox error={player.error} onRetry={player.reload} />
  if (matches.error) return <ErrorBox error={matches.error} onRetry={matches.reload} />

  const data = player.data
  const [firstName, ...rest] = (data.name || '').split(' ')
  const energyMax = data.vip_active ? ENERGY_MAX_VIP : ENERGY_MAX
  const nextMatch = matches.data.leagues.map((l) => l.next_match).find(Boolean)
  const club = team.error ? null : team.data?.club

  const inv = inventory.error ? null : inventory.data
  const equippedIds = inv ? Object.values(inv.equipped).filter(Boolean) : []
  const itemById = (id) => inv?.items.find((i) => i.id === id)

  const act = async (fn) => {
    setBusy(true)
    try {
      await fn()
      setOpenItem(null)
      inventory.reload()
      player.reload() // full_power / money change with equipment
    } catch (e) {
      alert(e?.message || 'Помилка')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="p-4 space-y-4">
      {/* Hero card */}
      <Card accent="gold" className="relative overflow-hidden hero-streaks">
        {avatarArt(data.gender, data.position) && (
          <img
            src={avatarArt(data.gender, data.position)}
            alt=""
            className="absolute right-6 top-0 h-full w-3/5 object-cover object-top pointer-events-none [mask-image:linear-gradient(to_left,transparent_0%,black_25%,black_75%,transparent_100%)]"
          />
        )}
        <div className="relative flex justify-between min-h-[170px]">
          <div>
            <div className="h-display text-3xl leading-none text-white break-words max-w-[200px]">{firstName}</div>
            {rest.length > 0 && (
              <div className="h-display text-[44px] leading-[1.05] text-gold glow-gold break-words max-w-[210px] tracking-tight">{rest.join(' ')}</div>
            )}
            {data.vip_active && (
              <span className="inline-block mt-2 h-display text-xs text-gold border border-gold/60 rounded-full px-2 py-0.5">
                ★ VIP
              </span>
            )}
          </div>
          <div className="flex flex-col items-end gap-2">
            <span
              className="w-14 h-14 rounded-full border-2 border-neon ring-glow-neon bg-pitch/60 flex items-center justify-center h-display text-xl text-neon"
              title={data.position}
            >
              {POSITION_SHORT[data.position] || data.position}
            </span>
            {data.level != null && (
              <span className="h-display text-sm text-neon border border-neon/50 bg-pitch/60 rounded-lg px-2 py-0.5">
                {data.level} рів.
              </span>
            )}
          </div>
        </div>
        <div className="relative flex items-end justify-end gap-3 mt-1">
          <span className="h-display text-base text-white/85 mb-2.5">Сила</span>
          <span className="h-display text-7xl leading-none text-gold glow-gold">
            {Math.round(data.full_power)}
          </span>
        </div>
      </Card>

      {/* XP progress + stat bars (compact — Max 23.07) */}
      <Card>
        {data.exp_next != null && (
          <div className="mb-3">
            <div className="flex items-baseline justify-between mb-1">
              <span className="text-muted text-[11px] uppercase tracking-wider">Досвід · рівень {data.level}</span>
              <span className="h-display text-xs text-neon">{data.exp}/{data.exp_next} XP</span>
            </div>
            <div className="h-1.5 bg-card2 rounded-full overflow-hidden">
              <div
                className="h-full bar-neon rounded-full"
                style={{ width: `${Math.max(0, Math.min(100, ((data.exp - data.exp_floor) / (data.exp_next - data.exp_floor)) * 100))}%` }}
              />
            </div>
          </div>
        )}
        {(() => {
          const statMax = Math.max(100, ...Object.values(data.stats))
          return STATS.map(({ key, label, Icon }) => (
            <StatBar key={key} label={label} value={data.stats[key]} max={statMax} icon={<Icon size={18} />} dense />
          ))
        })()}
      </Card>

      <EnergyBar value={data.energy} max={energyMax} />

      {/* Equipment slots */}
      <Card>
        <div className="flex items-center justify-between mb-2">
          <span className="h-display text-sm text-white/85 uppercase tracking-wider">Екіпірування</span>
          <button onClick={() => goTo('shop')} className="text-neon text-xs h-display">Магазин ›</button>
        </div>
        <div className="grid grid-cols-4 gap-2">
          {SLOTS.map(({ category, field, label }) => {
            const equippedId = inv?.equipped?.[field]
            const item = equippedId ? itemById(equippedId) : null
            return (
              <button
                key={category}
                onClick={() => (item ? setOpenItem(item) : goTo('shop'))}
                className={`aspect-square rounded-xl flex flex-col items-center justify-center gap-1 px-1 ${
                  item
                    ? 'border border-gold/60 ring-glow-gold bg-card2'
                    : 'border border-dashed border-white/20 bg-pitch/40'
                }`}
              >
                {item && gearArt(item.name) ? (
                  <img src={gearArt(item.name)} alt="" className="w-9 h-9 object-contain" />
                ) : (
                  <IconShirt size={22} className={item ? 'text-gold' : 'text-muted'} />
                )}
                <span className={`h-display text-[9px] uppercase leading-tight text-center ${item ? 'text-white' : 'text-muted'}`}>
                  {item ? item.name : label}
                </span>
              </button>
            )
          })}
        </div>
        {inv && inv.items.filter((i) => !equippedIds.includes(i.id)).length > 0 && (
          <div className="mt-3">
            <div className="text-muted text-[11px] uppercase tracking-wider mb-1.5">Інвентар</div>
            <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
              {inv.items.filter((i) => !equippedIds.includes(i.id)).map((i) => (
                <button
                  key={i.id}
                  onClick={() => setOpenItem(i)}
                  className="shrink-0 rounded-lg border border-neon/40 bg-card2 px-2.5 py-1.5 flex items-center gap-1.5"
                >
                  {gearArt(i.name) ? (
                    <img src={gearArt(i.name)} alt="" className="w-5 h-5 object-contain" />
                  ) : (
                    <IconShirt size={16} className="text-neon" />
                  )}
                  <span className="h-display text-[11px] text-white/90 max-w-[90px] truncate">{i.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </Card>

      {/* Club */}
      <Card className="cursor-pointer" onClick={() => goTo?.('team')}>
        {club ? (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span className="w-14 h-14 rounded-full border border-white/15 bg-card2 overflow-hidden shrink-0 flex items-center justify-center">
                {clubCrest(club.name) ? (
                  <img src={clubCrest(club.name)} alt="" className="w-full h-full object-cover" />
                ) : (
                  <span className="h-display text-lg">{(club.name || '?')[0]}</span>
                )}
              </span>
              <div className="min-w-0">
                <div className="h-display text-xl leading-tight truncate">{club.name}</div>
                <div className="text-muted text-[11px] uppercase tracking-wider">Сила команди</div>
                <div className="h-display text-xl text-gold glow-gold leading-none">
                  {Math.round(club.total_power).toLocaleString('uk-UA')}
                </div>
              </div>
            </div>
            {club.members?.length > 0 && (
              <div className="flex gap-1.5 overflow-x-auto pb-1 -mx-1 px-1">
                {club.members.map((m) => (
                  <span
                    key={m.user_id}
                    title={m.name}
                    className={`w-9 h-9 rounded-full shrink-0 overflow-hidden border ${
                      m.is_me ? 'border-gold ring-glow-gold' : 'border-neon/70'
                    } bg-card2 flex items-center justify-center`}
                  >
                    {avatarArt(m.gender || 'MAN', m.position) ? (
                      <img src={avatarArt(m.gender || 'MAN', m.position)} alt="" className="w-full h-full object-cover object-top" />
                    ) : (
                      <span className="h-display text-xs text-white/80">{(m.name || '?')[0]}</span>
                    )}
                  </span>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <span className="text-muted text-sm">Ти без команди</span>
            <span className="text-neon text-sm h-display">Знайти команду ›</span>
          </div>
        )}
      </Card>

      {/* Next match */}
      <Card accent="gold">
        <div className="flex items-center gap-3">
          <IconCalendar size={30} className="text-gold shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="h-display text-sm text-white/85 leading-none">Наступний матч</div>
            {nextMatch ? (
              <div className="h-display text-4xl text-gold glow-gold leading-tight">
                {fmtClock(nextMatch.time_to_start)}
              </div>
            ) : (
              <div className="text-muted text-xs mt-1.5">Немає запланованих матчів</div>
            )}
          </div>
          <CtaButton onClick={() => goTo('matches')}>
            {nextMatch ? 'Готуватися до матчу ›' : 'До матчів ›'}
          </CtaButton>
        </div>
      </Card>

      {openItem && (
        <ItemSheet
          item={openItem}
          isEquipped={equippedIds.includes(openItem.id)}
          busy={busy}
          onEquip={() => act(() => equipItem(openItem.id))}
          onUnequip={() => act(() => unequipItem(openItem.category))}
          onSell={() => act(() => sellItem(openItem.id))}
          onClose={() => setOpenItem(null)}
        />
      )}
    </div>
  )
}
