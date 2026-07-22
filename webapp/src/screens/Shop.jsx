import { useState } from 'react'
import { getShop, createInvoice, buyItem, openInvoice } from '../api'
import { useApi } from '../hooks'
import { Card, Loading, ErrorBox, CtaButton, PillTabs, Banner } from '../ui'
import { IconShirt, IconBox, IconBolt, IconCoin, IconStar } from '../icons'
import { art, gearArt } from '../assets/art'

const BOX_ART = { // API box keys (small_box/medium_box/large_box/new_member_box) -> art slugs
  small: 'box-small', medium: 'box-medium', large: 'box-premium', new_member: 'box-newbie',
}
function boxArt(key) {
  const k = String(key).toLowerCase()
  const hit = Object.keys(BOX_ART).find((n) => k.includes(n))
  return art[hit ? BOX_ART[hit] : 'box-small'] || null
}

function Thumb({ src, size = 'w-12 h-12' }) {
  if (!src) return null
  return <img src={src} alt="" className={`${size} rounded-xl object-cover border border-white/10 shrink-0`} />
}

const TABS = [
  { key: 'items', label: 'Речі', icon: <IconShirt size={16} /> },
  { key: 'boxes', label: 'Бокси', icon: <IconBox size={16} /> },
  { key: 'energy', label: 'Енергія', icon: <IconBolt size={16} /> },
  { key: 'coins', label: 'Монети', icon: <IconCoin size={16} /> },
  { key: 'vip', label: 'VIP', icon: <IconStar size={16} /> },
]

const POSITIONS = ['Нападник', 'Півзахисник', 'Захисник', 'Воротар']

function Price({ children }) {
  return <span className="h-display text-lg text-gold glow-gold whitespace-nowrap">{children}</span>
}

export default function Shop() {
  const { data, error, loading, reload } = useApi(getShop)
  const [tabIdx, setTabIdx] = useState(0)
  const [busy, setBusy] = useState(null)
  const [message, setMessage] = useState(null)
  const [pickPosition, setPickPosition] = useState(false)

  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  const tab = TABS[tabIdx].key
  const ownedIds = new Set(data.me.owned_items.map((i) => i.id))

  const pay = async (key, product_type, product_key) => {
    setBusy(key)
    setMessage(null)
    try {
      const { url } = await createInvoice(product_type, product_key)
      openInvoice(url)
      setMessage('Рахунок відкрито. Після оплати баланс оновиться автоматично.')
    } catch (e) {
      setMessage(e.message)
    } finally {
      setBusy(null)
    }
  }

  const purchaseItem = async (item, luxe) => {
    const key = `item-${luxe ? 'luxe' : 'std'}-${item.id}`
    setBusy(key)
    setMessage(null)
    try {
      await buyItem(item.id, luxe)
      setMessage(`Куплено: ${item.name} ✓`)
      reload()
    } catch (e) {
      setMessage(e.message)
    } finally {
      setBusy(null)
    }
  }

  const ItemRow = ({ item, luxe }) => {
    const key = `item-${luxe ? 'luxe' : 'std'}-${item.id}`
    const owned = !luxe && ownedIds.has(item.id)
    const affordable = data.me.money >= item.price && data.me.level >= item.level_required
    return (
      <Card className="flex justify-between items-center gap-3 py-3">
        <Thumb src={gearArt(item.name)} />
        <div className="min-w-0 flex-1">
          <div className="h-display text-base truncate">{item.name}</div>
          <div className="text-muted text-xs">
            Рівень {item.level_required}+ · +{Object.values(item.stats).reduce((a, b) => a + b, 0)} до статів
            {owned && <span className="text-neon"> · у тебе є</span>}
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Price>{item.price} 💰</Price>
          <CtaButton
            color="gold"
            disabled={busy === key || !affordable}
            onClick={() => purchaseItem(item, luxe)}
          >
            {busy === key ? '…' : 'Купити'}
          </CtaButton>
        </div>
      </Card>
    )
  }

  return (
    <div className="p-4 space-y-4">
      <Banner src={art['banner-shop']}>
        <div className="flex justify-between items-end w-full">
          <span className="h-display text-2xl text-gold glow-gold">Магазин</span>
          <span className="text-sm text-white/90">⚡ {data.me.energy} · 💰 {data.me.money}</span>
        </div>
      </Banner>

      <PillTabs tabs={TABS} active={tabIdx} onSelect={setTabIdx} />

      {message && (
        <div className="text-sm text-gold border border-gold/40 ring-glow-gold rounded-xl p-3">{message}</div>
      )}

      {tab === 'items' && (
        <div className="space-y-2">
          {data.items.map((item) => <ItemRow key={`s${item.id}`} item={item} luxe={false} />)}
          <div className="h-display text-lg text-neon glow-neon pt-2">Ексклюзив</div>
          {data.luxe_items.map((item) => <ItemRow key={`l${item.id}`} item={item} luxe={true} />)}
        </div>
      )}

      {tab === 'boxes' && (
        <div className="space-y-2">
          {data.boxes.map((box) => (
            <Card key={box.key} className="flex justify-between items-center gap-3 py-3">
              <Thumb src={boxArt(box.key)} size="w-14 h-14" />
              <div className="flex-1">
                <div className="h-display text-base">{box.name_lootbox}</div>
                <div className="text-muted text-xs">
                  ⚡ {box.min_energy}–{box.max_energy} · 💰 {box.min_money}–{box.max_money} · 📈 {box.min_exp}–{box.max_exp} XP
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <Price>{box.price} грн</Price>
                <CtaButton disabled={busy === box.key} onClick={() => pay(box.key, 'box', box.key)}>
                  {busy === box.key ? '…' : 'Купити'}
                </CtaButton>
              </div>
            </Card>
          ))}
        </div>
      )}

      {tab === 'energy' && (
        <div className="grid grid-cols-2 gap-3">
          {data.energy.map((pack) => (
            <Card key={pack.amount} className="text-center py-4">
              {art['energy'] && <img src={art['energy']} alt="" className="w-16 h-16 mx-auto mb-2 rounded-xl object-cover" />}
              <div className="h-display text-2xl text-neon glow-neon mb-1">⚡ {pack.amount}</div>
              <div className="mb-2"><Price>{pack.price_uah} грн</Price></div>
              <CtaButton
                className="w-full"
                disabled={busy === `en-${pack.amount}`}
                onClick={() => pay(`en-${pack.amount}`, 'energy', pack.amount)}
              >
                {busy === `en-${pack.amount}` ? '…' : 'Купити'}
              </CtaButton>
            </Card>
          ))}
        </div>
      )}

      {tab === 'coins' && (
        <div className="grid grid-cols-2 gap-3">
          {data.coins.map((pack) => (
            <Card key={pack.key} className="text-center py-4">
              {art['coins-small'] && (
                <img
                  src={pack.coins >= 1000 ? art['coins-large'] : art['coins-small']}
                  alt="" className="w-16 h-16 mx-auto mb-2 rounded-xl object-cover"
                />
              )}
              <div className="h-display text-2xl text-gold glow-gold mb-1">💰 {pack.coins}</div>
              <div className="mb-2"><Price>{pack.price_uah} грн</Price></div>
              <CtaButton
                color="gold"
                className="w-full"
                disabled={busy === pack.key}
                onClick={() => pay(pack.key, 'coins', pack.key)}
              >
                {busy === pack.key ? '…' : 'Купити'}
              </CtaButton>
            </Card>
          ))}
        </div>
      )}

      {tab === 'vip' && (
        <div className="space-y-2">
          {data.vip.map((pack) => (
            <Card key={pack.key} accent="gold" className="flex justify-between items-center gap-3 py-3">
              <Thumb src={art['vip']} />
              <div className="h-display text-base flex-1">⭐ VIP на {pack.duration_days} днів</div>
              <div className="flex items-center gap-2 shrink-0">
                <Price>{pack.price_uah} грн</Price>
                <CtaButton color="gold" disabled={busy === pack.key} onClick={() => pay(pack.key, 'vip', pack.key)}>
                  {busy === pack.key ? '…' : 'Купити'}
                </CtaButton>
              </div>
            </Card>
          ))}

          <Card className="py-3">
            <div className="flex justify-between items-center gap-3">
              <Thumb src={art['changepos']} />
              <div className="h-display text-base flex-1">🔄 Зміна позиції</div>
              <div className="flex items-center gap-2 shrink-0">
                <Price>{data.change_position_price} грн</Price>
                <CtaButton disabled={!!busy} onClick={() => setPickPosition((v) => !v)}>
                  Обрати
                </CtaButton>
              </div>
            </div>
            {pickPosition && (
              <div className="grid grid-cols-2 gap-2 mt-3">
                {POSITIONS.map((pos) => (
                  <button
                    key={pos}
                    disabled={busy === `pos-${pos}`}
                    onClick={() => pay(`pos-${pos}`, 'change_position', pos)}
                    className="h-display text-sm border border-neon/50 text-neon rounded-xl px-3 py-2 disabled:opacity-40"
                  >
                    {busy === `pos-${pos}` ? '…' : pos}
                  </button>
                ))}
              </div>
            )}
          </Card>

          <Card className="flex justify-between items-center gap-3 py-3">
            <Thumb src={art['key']} />
            <div className="h-display text-base flex-1">🔑 Ключ тренування</div>
            <div className="flex items-center gap-2 shrink-0">
              <Price>{data.training_key_price_uah} грн</Price>
              <CtaButton disabled={busy === 'key'} onClick={() => pay('key', 'training_key')}>
                {busy === 'key' ? '…' : 'Купити'}
              </CtaButton>
            </div>
          </Card>
        </div>
      )}

      <div className="text-muted text-xs text-center pb-2">
        Оплата — Monobank. Рахунок відкривається у браузері, покупка зараховується автоматично.
      </div>
    </div>
  )
}
