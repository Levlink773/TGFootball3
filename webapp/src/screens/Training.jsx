import { useEffect, useState } from 'react'
import { getTraining } from '../api'
import { useApi, fmtCountdown } from '../hooks'
import { Card, SectionTitle, Loading, ErrorBox } from '../ui'

function Countdown({ seconds }) {
  const [left, setLeft] = useState(seconds)
  useEffect(() => {
    setLeft(seconds)
    const t = setInterval(() => setLeft((v) => Math.max(0, v - 1)), 1000)
    return () => clearInterval(t)
  }, [seconds])
  return <span className="h-display text-neon glow-neon">{fmtCountdown(left)}</span>
}

export default function Training() {
  const { data, error, loading, reload } = useApi(getTraining)
  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  return (
    <div className="p-4 space-y-4">
      <Card accent="gold">
        <SectionTitle>🏋️ Тренування</SectionTitle>
        {data.in_training && data.training ? (
          <div className="flex justify-between items-center">
            <div>
              <div className="text-sm">Тренуємо: <b>{data.training.stats}</b></div>
              <div className="text-muted text-xs">до завершення</div>
            </div>
            <Countdown seconds={data.training.seconds_left} />
          </div>
        ) : (
          <div className="text-muted text-sm">
            Персонаж не тренується. Почни тренування у боті — вибір характеристики та тривалості.
          </div>
        )}
      </Card>

      <Card>
        <SectionTitle accent="neon">🎯 Тренер (QTE)</SectionTitle>
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm">Ключі тренувань</span>
          <span className="h-display text-xl text-gold glow-gold">{data.training_keys}/3</span>
        </div>
        {data.trainer.joined_today ? (
          <div className="text-sm">
            Сьогодні зіграно · рахунок: <b className="text-neon">{data.trainer.today_score}</b>
            {!data.trainer.session_ended && <span className="text-muted"> (сесія триває)</span>}
          </div>
        ) : (
          <div className="text-muted text-sm">Сьогодні ще не грав із тренером</div>
        )}
      </Card>

      <Card>
        <SectionTitle>🏫 Навчальний центр</SectionTitle>
        {data.education?.can_claim ? (
          <div className="text-neon">🎁 Нагорода доступна — забери в боті!</div>
        ) : data.education ? (
          <div className="flex justify-between items-center">
            <span className="text-muted text-sm">До наступної нагороди</span>
            <Countdown seconds={data.education.seconds_left} />
          </div>
        ) : null}
      </Card>

      <Card>
        <div className="flex justify-between items-center">
          <span className="text-muted text-sm">⚡ Енергія</span>
          <span className="h-display text-xl text-neon">{data.energy}</span>
        </div>
      </Card>
    </div>
  )
}
