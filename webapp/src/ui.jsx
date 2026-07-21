export function Card({ children, className = '', accent }) {
  const border = accent === 'gold'
    ? 'border-gold/60 shadow-[0_0_18px_rgba(255,215,0,0.15)]'
    : accent === 'neon'
      ? 'border-neon/60 shadow-[0_0_18px_rgba(0,255,255,0.15)]'
      : 'border-white/5'
  return (
    <div className={`bg-card rounded-xl border ${border} p-4 ${className}`}>
      {children}
    </div>
  )
}

export function SectionTitle({ children, accent = 'gold' }) {
  return (
    <h2 className={`h-display text-xl mb-3 ${accent === 'gold' ? 'text-gold glow-gold' : 'text-neon glow-neon'}`}>
      {children}
    </h2>
  )
}

export function Loading() {
  return <div className="text-muted text-center py-10 animate-pulse">Завантаження…</div>
}

export function ErrorBox({ error, onRetry }) {
  return (
    <div className="text-center py-10">
      <div className="text-red-400 mb-3">{error?.message || 'Помилка'}</div>
      {onRetry && (
        <button onClick={onRetry} className="text-neon border border-neon/50 rounded-lg px-4 py-2">
          Спробувати ще
        </button>
      )}
    </div>
  )
}

export function StatBar({ label, value, max = 100 }) {
  return (
    <div className="mb-2">
      <div className="flex justify-between text-xs text-muted mb-1">
        <span>{label}</span>
        <span className="text-white font-semibold">{value}</span>
      </div>
      <div className="h-1.5 bg-card2 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-gold to-neon"
          style={{ width: `${Math.min(100, (value / max) * 100)}%` }}
        />
      </div>
    </div>
  )
}
