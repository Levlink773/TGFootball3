import { useState } from 'react'
import { completeTutorial } from '../api'
import { CtaButton } from '../ui'
import { art } from '../assets/art'

// Guided onboarding: each step opens the real tab and explains it.
// `highlight` tells App which nav tab to pulse.
const STEPS = [
  {
    tab: 'home', highlight: null, artKey: 'tut-1-welcome',
    title: 'Вітаємо у TG Football!',
    text: 'Це твоя футбольна кар’єра: прокачуй гравця, грай матчі, веди клуб до вершини ліги. Пройдемо коротку екскурсію?',
  },
  {
    tab: 'player', highlight: 'player', artKey: 'tut-2-player',
    title: 'Твій гравець',
    text: 'Вкладка «Гравець» — твій профіль: техніка, удари, відбір, швидкість і витривалість. Разом вони дають Силу гравця.',
  },
  {
    tab: 'training', highlight: 'training', artKey: 'tut-3-training',
    title: 'Тренування',
    text: 'Сила росте на тренуваннях. Тренуй окремі характеристики, грай із тренером (QTE) і забирай нагороди навчального центру.',
  },
  {
    tab: 'shop', highlight: 'shop', artKey: 'tut-4-shop',
    title: 'Магазин',
    text: 'Екіпіровка додає стати одразу. Купуй форму за монети, відкривай бокси, поповнюй енергію.',
  },
  {
    tab: 'matches', highlight: 'matches', artKey: 'tut-5-match',
    title: 'Матчі та бліц',
    text: 'Реєструйся на матчі ліги та щоденні бліц-турніри. Перемоги дають монети, досвід і місце в Залі Слави. Успіхів!',
  },
]

export default function Tutorial({ goTo, setHighlight, onDone }) {
  const [step, setStep] = useState(0)
  const [busy, setBusy] = useState(false)
  const s = STEPS[step]
  const last = step === STEPS.length - 1

  const finish = async () => {
    setBusy(true)
    try {
      await completeTutorial()
    } catch {
      // non-blocking: server flag will be retried next launch; local flag hides overlay
    }
    localStorage.setItem('tgf_tutorial_done', '1')
    setHighlight(null)
    goTo('home')
    onDone()
  }

  const next = () => {
    if (last) return finish()
    const n = STEPS[step + 1]
    goTo(n.tab)
    setHighlight(n.highlight)
    setStep(step + 1)
  }

  const intro = step === 0
  return (
    // Bottom sheet, no full-screen dim: the tab being explained stays visible above.
    <div className="fixed inset-x-0 bottom-16 z-30 flex justify-center pointer-events-none">
      <div className="pointer-events-auto w-full max-w-[422px] px-3 pb-2">
        <div className="bg-card/95 backdrop-blur border border-gold ring-glow-gold rounded-2xl overflow-hidden shadow-[0_-8px_30px_rgba(0,0,0,0.6)]">
          {intro && art[s.artKey] && (
            <img src={art[s.artKey]} alt="" className="w-full aspect-[21/9] object-cover" />
          )}
          <div className="p-3.5">
            <div className="flex items-start gap-3">
              {!intro && art[s.artKey] && (
                <img src={art[s.artKey]} alt="" className="w-16 h-16 rounded-xl object-cover border border-white/10 shrink-0" />
              )}
              <div className="min-w-0">
                <div className="h-display text-lg text-gold glow-gold leading-tight">{s.title}</div>
                <p className="text-[13px] leading-snug text-white/85 mt-0.5">{s.text}</p>
              </div>
            </div>
            <div className="flex items-center justify-between mt-3">
              <div className="flex gap-1.5">
                {STEPS.map((_, i) => (
                  <span key={i} className={`w-2 h-2 rounded-full ${i === step ? 'bg-gold' : 'bg-white/20'}`} />
                ))}
              </div>
              <div className="flex gap-2 items-center">
                {!last && (
                  <button onClick={finish} disabled={busy} className="text-muted text-sm px-2 py-2">
                    Пропустити
                  </button>
                )}
                <CtaButton color="gold" disabled={busy} onClick={next}>
                  {busy ? '…' : last ? 'Почати гру!' : 'Далі ›'}
                </CtaButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
