import { useEffect, useState } from 'react'
import Home from './screens/Home'
import Player from './screens/Player'
import Matches from './screens/Matches'
import Training from './screens/Training'
import League from './screens/League'
import HallOfFame from './screens/HallOfFame'
import Shop from './screens/Shop'

const TABS = [
  { key: 'player', label: 'Гравець', icon: '🏃' },
  { key: 'matches', label: 'Матчі', icon: '⚽' },
  { key: 'training', label: 'Трен-ня', icon: '🏋️' },
  { key: 'league', label: 'Ліга', icon: '🏆' },
  { key: 'fame', label: 'Зал Слави', icon: '🌟' },
]

const SCREENS = {
  home: Home,
  player: Player,
  matches: Matches,
  training: Training,
  league: League,
  fame: HallOfFame,
  shop: Shop,
}

export default function App() {
  const [tab, setTab] = useState('home')
  const Screen = SCREENS[tab]

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    tg?.ready?.()
    tg?.expand?.()
  }, [])

  return (
    <div className="max-w-[422px] mx-auto min-h-full flex flex-col">
      <header className="flex items-center justify-between px-4 py-3 sticky top-0 z-10 bg-pitch/90 backdrop-blur border-b border-white/5">
        <button onClick={() => setTab('home')} className="h-display text-lg text-gold glow-gold">
          ⚽ TG FOOTBALL
        </button>
        <button
          onClick={() => setTab('shop')}
          className={`text-xl ${tab === 'shop' ? 'drop-shadow-[0_0_8px_rgba(255,215,0,0.7)]' : ''}`}
          aria-label="Магазин"
        >
          🛒
        </button>
      </header>

      <main className="flex-1 pb-20">
        <Screen goTo={setTab} />
      </main>

      <nav className="fixed bottom-0 inset-x-0 z-10 border-t border-white/10 bg-pitch/95 backdrop-blur">
        <div className="max-w-[422px] mx-auto flex">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`flex-1 py-2.5 flex flex-col items-center gap-0.5 text-[10px] uppercase h-display ${
                tab === t.key ? 'text-gold glow-gold' : 'text-muted'
              }`}
            >
              <span className={`text-lg ${tab === t.key ? 'drop-shadow-[0_0_8px_rgba(255,215,0,0.7)]' : 'grayscale opacity-70'}`}>
                {t.icon}
              </span>
              {t.label}
              {tab === t.key && <span className="w-6 h-0.5 bg-gold rounded-full mt-0.5" />}
            </button>
          ))}
        </div>
      </nav>
    </div>
  )
}
