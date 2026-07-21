import { useState } from 'react'
import { getShop } from '../api'
import { useApi } from '../hooks'
import { Card, Loading, ErrorBox } from '../ui'

const TABS = [
  { key: 'items', label: '👕 Речі' },
  { key: 'boxes', label: '📦 Бокси' },
  { key: 'energy', label: '⚡ Енергія' },
  { key: 'coins', label: '💰 Монети' },
  { key: 'vip', label: '⭐ VIP' },
]

function Price({ children }) {
  return <span className="h-display text-gold glow-gold whitespace-nowrap">{children}</span>
}

export default function Shop() {
  const { data, error, loading, reload } = useApi(getShop)
  const [tab, setTab] = useState('items')

  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  const ownedIds = new Set(data.me.owned_items.map((i) => i.id))

  return (
    <div className="p-4 space-y-4">
      <div className="flex justify-between items-center">
        <div className="h-display text-xl text-gold glow-gold">🛒 Магазин</div>
        <div className="text-sm text-muted">⚡ {data.me.energy} · 💰 {data.me.money}</div>
      </div>

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

      {tab === 'items' && (
        <div className="space-y-2">
          {data.items.map((item) => (
            <Card key={item.id} className="flex justify-between items-center py-3">
              <div>
                <div className="h-display text-sm">{item.name}</div>
                <div className="text-muted text-xs">
                  Рівень {item.level_required}+ · {Object.values(item.stats).reduce((a, b) => a + b, 0)} до статів
                  {ownedIds.has(item.id) && <span className="text-neon"> · у тебе є</span>}
                </div>
              </div>
              <Price>{item.price} 💰</Price>
            </Card>
          ))}
        </div>
      )}

      {tab === 'boxes' && (
        <div className="space-y-2">
          {data.boxes.map((box) => (
            <Card key={box.key} className="flex justify-between items-center py-3">
              <div>
                <div className="h-display text-sm">{box.name_lootbox}</div>
                <div className="text-muted text-xs">
                  ⚡ {box.min_energy}–{box.max_energy} · 💰 {box.min_money}–{box.max_money} · 📈 {box.min_exp}–{box.max_exp} XP
                </div>
              </div>
              <Price>{box.price} грн</Price>
            </Card>
          ))}
        </div>
      )}

      {tab === 'energy' && (
        <div className="grid grid-cols-2 gap-3">
          {data.energy.map((pack) => (
            <Card key={pack.amount} className="text-center py-4">
              <div className="h-display text-2xl text-neon glow-neon mb-1">⚡ {pack.amount}</div>
              <Price>{pack.price_uah} грн</Price>
            </Card>
          ))}
        </div>
      )}

      {tab === 'coins' && (
        <div className="grid grid-cols-2 gap-3">
          {data.coins.map((pack) => (
            <Card key={pack.key} className="text-center py-4">
              <div className="h-display text-2xl text-gold glow-gold mb-1">💰 {pack.coins}</div>
              <Price>{pack.price_uah} грн</Price>
            </Card>
          ))}
        </div>
      )}

      {tab === 'vip' && (
        <div className="space-y-2">
          {data.vip.map((pack) => (
            <Card key={pack.key} accent="gold" className="flex justify-between items-center py-3">
              <div className="h-display text-sm">⭐ VIP на {pack.duration_days} днів</div>
              <Price>{pack.price_uah} грн</Price>
            </Card>
          ))}
          <Card className="flex justify-between items-center py-3">
            <div className="h-display text-sm">🔄 Зміна позиції</div>
            <Price>{data.change_position_price} грн</Price>
          </Card>
          <Card className="flex justify-between items-center py-3">
            <div className="h-display text-sm">🔑 Ключ тренування</div>
            <Price>{data.training_key_price_uah} грн</Price>
          </Card>
        </div>
      )}

      <div className="text-muted text-xs text-center pb-2">
        Оплата — Monobank, як у боті. Покупки в застосунку підключимо на наступному етапі.
      </div>
    </div>
  )
}
