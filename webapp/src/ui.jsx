import { IconBolt } from './icons'

export function Card({ children, className = '', accent, onClick }) {
  const border = accent === 'gold'
    ? 'border-gold/60 ring-glow-gold'
    : accent === 'neon'
      ? 'border-neon/60 ring-glow-neon'
      : 'border-white/5'
  return (
    <div onClick={onClick} className={`bg-card rounded-2xl border ${border} p-4 ${className}`}>
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

// v1-neon stat row: gold icon · label · cyan glowing bar · cyan value
export function StatBar({ label, value, max = 100, icon = null }) {
  return (
    <div className="flex items-center gap-3 py-2">
      {icon && <span className="text-gold shrink-0">{icon}</span>}
      <span className="h-display text-sm w-28 shrink-0">{label}</span>
      <div className="flex-1 h-2 bg-card2 rounded-full overflow-hidden">
        <div className="h-full rounded-full bar-neon" style={{ width: `${Math.min(100, (value / max) * 100)}%` }} />
      </div>
      <span className="h-display text-lg text-neon glow-neon w-9 text-right shrink-0">{value}</span>
    </div>
  )
}

// Segmented cyan energy bar (frame 1)
export function EnergyBar({ value, max }) {
  const SEGMENTS = 14
  const lit = Math.round((Math.min(value, max) / max) * SEGMENTS)
  return (
    <div className="flex items-center gap-3 bg-card rounded-2xl border border-neon/50 ring-glow-neon px-4 py-3">
      <IconBolt size={22} className="text-neon shrink-0" />
      <div className="h-display text-2xl shrink-0">
        <span className="text-neon glow-neon">{value}</span>
        <span className="text-muted text-base"> /{max}</span>
      </div>
      <div className="flex-1 flex gap-1">
        {Array.from({ length: SEGMENTS }, (_, i) => (
          <span
            key={i}
            className={`flex-1 h-4 rounded-[3px] ${i < lit ? 'bar-neon' : 'bg-card2'}`}
          />
        ))}
      </div>
    </div>
  )
}

// Segmented pill top-tabs with icon + glow border on active (frame 3)
export function PillTabs({ tabs, active, onSelect }) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
      {tabs.map((t, i) => {
        const isActive = i === active
        return (
          <button
            key={t.key ?? i}
            onClick={() => onSelect(i)}
            className={`h-display flex items-center gap-1.5 whitespace-nowrap text-sm rounded-xl px-3 py-2 border transition-colors ${
              isActive
                ? 'text-gold border-gold ring-glow-gold bg-card'
                : 'text-neon/80 border-white/10'
            }`}
          >
            {t.icon}
            {t.label}
          </button>
        )
      })}
    </div>
  )
}

// "НАСТУПНИЙ ТУР · 21:00" bar with chevrons (frames 1+3)
export function NextBar({ icon, label, time, onClick, cta }) {
  return (
    <div
      onClick={onClick}
      className={`flex items-center gap-3 bg-card rounded-2xl border border-neon/50 ring-glow-neon px-4 py-3 ${onClick ? 'cursor-pointer' : ''}`}
    >
      {icon && <span className="text-gold shrink-0">{icon}</span>}
      <span className="h-display text-base flex-1">{label}</span>
      <span className="h-display text-2xl text-neon glow-neon">{time}</span>
      {cta ? cta : <span className="chevrons-r text-neon/70 w-8 h-4" />}
    </div>
  )
}

// Filled CTA: cyan block, black italic text, glow (frame 1 "ГОТУВАТИСЯ ДО МАТЧУ")
export function CtaButton({ children, onClick, disabled, color = 'neon', className = '' }) {
  const palette = color === 'gold'
    ? 'bg-gold text-black shadow-[0_0_18px_rgba(255,215,0,0.5)]'
    : 'bg-neon text-black shadow-[0_0_18px_rgba(0,255,255,0.5)]'
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`h-display text-base rounded-xl px-4 py-2.5 disabled:opacity-40 disabled:shadow-none ${palette} ${className}`}
    >
      {children}
    </button>
  )
}

// Circle badge with club crest art (fallback: initials)
export function InitialsBadge({ name, active, src }) {
  const initials = (name || '?')
    .split(/\s+/)
    .map((w) => w[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
  return (
    <span
      className={`w-9 h-9 rounded-full shrink-0 flex items-center justify-center h-display text-sm border overflow-hidden ${
        active ? 'border-neon text-neon ring-glow-neon' : 'border-white/15 text-white/80 bg-card2'
      }`}
    >
      {src ? <img src={src} alt="" className="w-full h-full object-cover" /> : initials}
    </span>
  )
}

// Screen-top hero banner strip (generated V1-neon art)
export function Banner({ src, children }) {
  if (!src) return null
  return (
    <div className="relative rounded-2xl overflow-hidden border border-white/10">
      <img src={src} alt="" className="w-full aspect-[21/9] object-cover" />
      {children && (
        <div className="absolute inset-0 flex items-end bg-gradient-to-t from-black/70 to-transparent p-3">
          {children}
        </div>
      )}
    </div>
  )
}
