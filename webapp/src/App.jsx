import { useEffect, useState } from 'react'
import Home from './screens/Home'
import Player from './screens/Player'
import Matches from './screens/Matches'
import Training from './screens/Training'
import League from './screens/League'
import HallOfFame from './screens/HallOfFame'
import Shop from './screens/Shop'
import Settings from './screens/Settings'
import { getPlayer } from './api'
import { useApi } from './hooks'
import { IconUser, IconBall, IconDumbbell, IconTrophy, IconStar, IconCart, IconGear, IconCoin, IconPlus } from './icons'

const TABS = [
  { key: 'player', label: 'Гравець', Icon: IconUser },
  { key: 'matches', label: 'Матчі', Icon: IconBall },
  { key: 'training', label: 'Трен-ня', Icon: IconDumbbell },
  { key: 'league', label: 'Ліга', Icon: IconTrophy },
  { key: 'fame', label: 'Зал Слави', Icon: IconStar },
]

const SCREENS = {
  home: Home,
  player: Player,
  matches: Matches,
  training: Training,
  league: League,
  fame: HallOfFame,
  shop: Shop,
  settings: Settings,
}

export default function App() {
  const [tab, setTab] = useState('home')
  const player = useApi(getPlayer)
  const Screen = SCREENS[tab]

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    tg?.ready?.()
    tg?.expand?.()
  }, [])

  // keep header balance fresh after purchases/registrations
  useEffect(() => { player.reload() }, [tab]) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="max-w-[422px] mx-auto min-h-full flex flex-col">
      <header className="flex items-center justify-between px-4 py-3 sticky top-0 z-10 bg-pitch/90 backdrop-blur border-b border-white/5">
        <button
          onClick={() => setTab('shop')}
          className="flex items-center gap-2 bg-card border border-gold/50 ring-glow-gold rounded-full pl-2 pr-1 py-1"
          aria-label="Баланс — відкрити магазин"
        >
          <IconCoin size={18} className="text-gold" />
          <span className="h-display text-base text-white">
            {player.data ? player.data.money.toLocaleString('uk-UA') : '…'}
          </span>
          <span className="w-6 h-6 rounded-full bg-gold text-black flex items-center justify-center">
            <IconPlus size={14} />
          </span>
        </button>

        <button onClick={() => setTab('home')} className="h-display text-lg text-gold glow-gold">
          TG FOOTBALL
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setTab('shop')}
            className={tab === 'shop' ? 'text-gold' : 'text-neon'}
            aria-label="Магазин"
          >
            <IconCart size={22} />
          </button>
          <button
            onClick={() => setTab('settings')}
            className={tab === 'settings' ? 'text-gold' : 'text-neon'}
            aria-label="Налаштування"
          >
            <IconGear size={22} />
          </button>
        </div>
      </header>

      <main className="flex-1 pb-20">
        <Screen goTo={setTab} />
      </main>

      <nav className="fixed bottom-0 inset-x-0 z-10 border-t border-white/10 bg-pitch/95 backdrop-blur">
        <div className="max-w-[422px] mx-auto flex">
          {TABS.map(({ key, label, Icon }) => {
            const active = tab === key
            return (
              <button
                key={key}
                onClick={() => setTab(key)}
                className={`flex-1 py-2.5 flex flex-col items-center gap-1 text-[10px] uppercase h-display ${
                  active ? 'text-gold glow-gold' : 'text-muted'
                }`}
              >
                <Icon size={22} className={active ? 'drop-shadow-[0_0_8px_rgba(255,215,0,0.8)]' : ''} />
                {label}
                <span className={`w-6 h-0.5 rounded-full ${active ? 'bg-gold shadow-[0_0_8px_rgba(255,215,0,0.8)]' : 'bg-transparent'}`} />
              </button>
            )
          })}
        </div>
      </nav>
    </div>
  )
}
