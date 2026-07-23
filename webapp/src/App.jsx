import { useEffect, useState } from 'react'
import Home from './screens/Home'
import Player from './screens/Player'
import Matches from './screens/Matches'
import Training from './screens/Training'
import League from './screens/League'
import HallOfFame from './screens/HallOfFame'
import Shop from './screens/Shop'
import Settings from './screens/Settings'
import Team from './screens/Team'
import Statistics from './screens/Statistics'
import Trainer from './screens/Trainer'
import Tutorial from './components/Tutorial'
import { getPlayer, getTutorial } from './api'
import { useApi } from './hooks'
import { IconUser, IconBall, IconDumbbell, IconTrophy, IconStar, IconCart, IconGear, IconCoin, IconPlus, IconHome } from './icons'

// Нижнє меню — «Головна» додана за запитом Max 23.07 (єдиний вхід на головну був через лого).
const TABS = [
  { key: 'home', label: 'Головна', Icon: IconHome },
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
  team: Team,
  stats: Statistics,
  trainer: Trainer,
}

export default function App() {
  const [tab, setTab] = useState('home')
  const [highlight, setHighlight] = useState(null)
  const [showTutorial, setShowTutorial] = useState(false)
  const player = useApi(getPlayer)
  const Screen = SCREENS[tab]

  // Server-driven onboarding: show once per account until /tutorial/complete succeeds.
  useEffect(() => {
    if (localStorage.getItem('tgf_tutorial_done')) return
    getTutorial().then((t) => { if (!t.completed) setShowTutorial(true) }).catch(() => {})
  }, [])

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
        {player.error?.status === 404 ? (
          <div className="p-6 text-center space-y-4 pt-16">
            <div className="h-display text-3xl text-gold glow-gold">Ласкаво просимо!</div>
            <p className="text-white/85 text-sm">
              У тебе ще немає футболіста. Повернись у чат бота і натисни
              <b> «СТВОРИТИ ПЕРСОНАЖА»</b> — це займе хвилину, і гра відкриється.
            </p>
            <button
              onClick={() => window.Telegram?.WebApp?.close?.()}
              className="h-display text-base rounded-xl px-5 py-2.5 bg-gold text-black shadow-[0_0_18px_rgba(255,215,0,0.5)]"
            >
              Відкрити чат бота
            </button>
          </div>
        ) : (
          <Screen goTo={setTab} />
        )}
      </main>

      {showTutorial && (
        <Tutorial goTo={setTab} setHighlight={setHighlight} onDone={() => setShowTutorial(false)} />
      )}

      <nav className="fixed bottom-0 inset-x-0 z-10 border-t border-white/10 bg-pitch/95 backdrop-blur">
        <div className="max-w-[422px] mx-auto flex">
          {TABS.map(({ key, label, Icon }) => {
            const active = tab === key
            const pulsed = highlight === key
            return (
              <button
                key={key}
                onClick={() => setTab(key)}
                className={`flex-1 py-2.5 flex flex-col items-center gap-1 text-[10px] uppercase h-display ${
                  active ? 'text-gold glow-gold' : 'text-muted'
                } ${pulsed ? 'animate-pulse text-neon' : ''}`}
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
