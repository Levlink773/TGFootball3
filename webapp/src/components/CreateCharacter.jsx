import { useMemo, useState } from 'react'
import { createCharacter, getCharacterOptions } from '../api'
import { useApi } from '../hooks'
import { Card, CtaButton, ErrorBox, Loading, StatBar } from '../ui'
import { avatarArt } from '../assets/art'
import { IconBall, IconUser } from '../icons'

const STEPS = ['name', 'gender', 'position', 'confirm']

const STAT_LABELS = {
  technique: 'Техніка',
  kicks: 'Удари',
  ball_selection: 'Відбір',
  speed: 'Швидкість',
  endurance: 'Витривалість',
}

function Stats({ stats }) {
  return (
    <div>
      {Object.entries(STAT_LABELS).map(([key, label]) => (
        <StatBar key={key} label={label} value={stats[key]} max={20} dense />
      ))}
    </div>
  )
}

function Choice({ active, onClick, children }) {
  return (
    <Card accent={active ? 'gold' : undefined} onClick={onClick} className="text-left">
      {children}
    </Card>
  )
}

/**
 * First-run registration, in the app instead of the bot chat.
 *
 * Positions and their starting stats come from GET /character/options rather than
 * being hardcoded here, so the numbers can't drift away from const_character.py.
 */
export default function CreateCharacter({ onCreated }) {
  const options = useApi(getCharacterOptions)
  const [step, setStep] = useState(0)
  const [name, setName] = useState('')
  const [gender, setGender] = useState(null)
  const [position, setPosition] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const opts = options.data
  const chosen = useMemo(
    () => opts?.positions.find((p) => p.key === position) || null,
    [opts, position],
  )
  const trimmed = name.trim().replace(/\s+/g, ' ')
  const nameOk = opts
    ? trimmed.length >= opts.name_min && trimmed.length <= opts.name_max
    : false

  if (options.loading) return <Loading />
  if (options.error) return <ErrorBox error={options.error} onRetry={options.reload} />

  const submit = async () => {
    setBusy(true)
    setError(null)
    try {
      const res = await createCharacter(trimmed, gender, position)
      // Deliberately not clearing busy on success: onCreated swaps this component
      // out, and leaving the button disabled until then prevents a double submit
      // during the parent's refetch.
      await onCreated(res.player)
    } catch (e) {
      setError(e)
      setBusy(false)
      setStep(STEPS.indexOf('confirm')) // stay on confirm so the choices can be edited
    }
  }

  const back = () => setStep((s) => Math.max(0, s - 1))
  const next = () => setStep((s) => s + 1)

  return (
    <div className="max-w-[422px] mx-auto min-h-full flex flex-col p-4 pb-8 gap-4">
      <div className="text-center pt-6 space-y-1">
        <div className="h-display text-lg text-gold glow-gold">TG FOOTBALL</div>
        <div className="h-display text-2xl text-white">Створи футболіста</div>
        <p className="text-muted text-xs">Крок {step + 1} з {STEPS.length}</p>
      </div>

      <div className="flex gap-1.5">
        {STEPS.map((s, i) => (
          <span
            key={s}
            className={`flex-1 h-1 rounded-full ${i <= step ? 'bar-neon' : 'bg-card2'}`}
          />
        ))}
      </div>

      {error && <ErrorBox error={error} />}

      {STEPS[step] === 'name' && (
        <div className="space-y-3">
          <p className="text-white/85 text-sm">Як тебе звати на полі?</p>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={opts.name_max}
            autoFocus
            placeholder="Ім'я футболіста"
            className="w-full bg-card border border-white/10 focus:border-neon focus:outline-none rounded-xl px-4 py-3 text-white h-display text-lg"
          />
          <p className="text-muted text-xs">
            Від {opts.name_min} до {opts.name_max} символів. Літери, цифри, пробіл, дефіс, апостроф.
          </p>
          <CtaButton onClick={next} disabled={!nameOk} className="w-full">
            Далі ›
          </CtaButton>
        </div>
      )}

      {STEPS[step] === 'gender' && (
        <div className="space-y-3">
          <p className="text-white/85 text-sm">Обери стать футболіста.</p>
          {opts.genders.map((g) => (
            <Choice
              key={g.key}
              active={gender === g.key}
              onClick={() => { setGender(g.key); next() }}
            >
              <div className="flex items-center gap-3">
                <IconUser size={22} className="text-gold shrink-0" />
                <span className="h-display text-lg">{g.label}</span>
              </div>
            </Choice>
          ))}
          <button onClick={back} className="text-muted text-sm w-full py-2">‹ Назад</button>
        </div>
      )}

      {STEPS[step] === 'position' && (
        <div className="space-y-3">
          <p className="text-white/85 text-sm">
            Позиція визначає стартові характеристики й роль у команді.
          </p>
          {opts.positions.map((p) => {
            const src = avatarArt(gender, p.label)
            return (
              <Choice
                key={p.key}
                active={position === p.key}
                onClick={() => { setPosition(p.key); next() }}
              >
                <div className="flex items-center gap-3 mb-2">
                  {src
                    ? <img src={src} alt="" className="w-12 h-12 rounded-full object-cover border border-white/15" />
                    : <IconBall size={22} className="text-gold shrink-0" />}
                  <span className="h-display text-lg">{p.label}</span>
                </div>
                <Stats stats={p.stats} />
              </Choice>
            )
          })}
          <button onClick={back} className="text-muted text-sm w-full py-2">‹ Назад</button>
        </div>
      )}

      {STEPS[step] === 'confirm' && chosen && (
        <div className="space-y-3">
          <Card accent="gold">
            <div className="flex items-center gap-3 mb-3">
              {avatarArt(gender, chosen.label) && (
                <img
                  src={avatarArt(gender, chosen.label)}
                  alt=""
                  className="w-16 h-16 rounded-full object-cover border border-gold/60"
                />
              )}
              <div>
                <div className="h-display text-xl text-white">{trimmed}</div>
                <div className="text-muted text-sm">{chosen.label}</div>
              </div>
            </div>
            <Stats stats={chosen.stats} />
          </Card>
          <CtaButton onClick={submit} disabled={busy} color="gold" className="w-full">
            {busy ? 'Створюємо…' : 'Почати кар’єру'}
          </CtaButton>
          <button
            onClick={back}
            disabled={busy}
            className="text-muted text-sm w-full py-2 disabled:opacity-40"
          >
            ‹ Змінити позицію
          </button>
        </div>
      )}
    </div>
  )
}
