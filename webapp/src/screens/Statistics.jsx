import { getStatistics } from '../api'
import { useApi } from '../hooks'
import { Card, SectionTitle, Loading, ErrorBox } from '../ui'

const CAREER_ROWS = [
  ['trainings', '🏋️ Тренувань'],
  ['match_registrations', '📝 Реєстрацій на матчі'],
  ['goals', '⚽ Голів'],
  ['blitz_played', '⚡ Бліців зіграно'],
  ['blitz_semifinals', '🥉 Півфіналів бліцу'],
  ['blitz_finals', '🥈 Фіналів бліцу'],
  ['blitz_wins', '🏆 Перемог у бліці'],
  ['mvp_2_plus', '⭐ MVP 2.0+'],
  ['mvp_25_plus', '🌟 MVP 2.5+'],
  ['mvp_3_plus', '💫 MVP 3.0+'],
]

export default function Statistics({ goTo }) {
  const { data, error, loading, reload } = useApi(getStatistics)
  if (loading) return <Loading />
  if (error) return <ErrorBox error={error} onRetry={reload} />

  return (
    <div className="p-4 space-y-4">
      <button onClick={() => goTo('home')} className="text-muted text-sm">‹ На головну</button>

      <div className="text-center">
        <div className="h-display text-3xl text-gold glow-gold">Статистика</div>
      </div>

      <div className="grid grid-cols-3 gap-3 text-center">
        <Card className="py-3">
          <div className="h-display text-2xl text-gold glow-gold">{data.progress.level}</div>
          <div className="text-muted text-[10px] uppercase">Рівень</div>
        </Card>
        <Card className="py-3">
          <div className="h-display text-2xl text-neon glow-neon">{data.progress.full_power}</div>
          <div className="text-muted text-[10px] uppercase">Сила</div>
        </Card>
        <Card className="py-3">
          <div className="h-display text-2xl text-white/90">{data.progress.exp}</div>
          <div className="text-muted text-[10px] uppercase">Досвід</div>
        </Card>
      </div>

      <Card>
        <SectionTitle accent="neon">Цей місяць</SectionTitle>
        <div className="flex justify-between text-center">
          <div>
            <div className="h-display text-xl text-white/90">{data.month.matches}</div>
            <div className="text-muted text-[10px] uppercase">Матчів</div>
          </div>
          <div>
            <div className="h-display text-xl text-gold">{data.month.goals}</div>
            <div className="text-muted text-[10px] uppercase">Голів</div>
          </div>
          <div>
            <div className="h-display text-xl text-neon">{data.month.mvp_score}</div>
            <div className="text-muted text-[10px] uppercase">MVP-бали</div>
          </div>
        </div>
      </Card>

      <Card className="p-0 overflow-hidden">
        <div className="px-4 pt-3"><SectionTitle>Кар'єра</SectionTitle></div>
        {CAREER_ROWS.map(([key, label]) => (
          <div key={key} className="flex justify-between px-4 py-2 border-t border-white/5">
            <span className="text-sm">{label}</span>
            <span className="h-display text-gold">{data.career[key]}</span>
          </div>
        ))}
      </Card>
    </div>
  )
}
