import { useCallback, useEffect, useState } from 'react'

// pollMs (optional): silently refetch on an interval — no loading flash, so
// polled data (training status, quests) can drive live UI without spinners.
export function useApi(fn, { pollMs } = {}) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  // Returns the promise so callers can await a refetch (the registration wizard
  // holds its busy state until the app is genuinely ready rather than flashing).
  const run = useCallback((silent) => {
    if (!silent) setLoading(true)
    setError(null)
    return fn()
      .then(setData)
      .catch(setError)
      .finally(() => { if (!silent) setLoading(false) })
  }, [fn])

  const reload = useCallback(() => run(false), [run])
  // Silent refetch: no loading flag, so a caller that re-renders on `loading`
  // (the App gate) doesn't tear its subtree down just to refresh a balance.
  const refresh = useCallback(() => run(true), [run])

  useEffect(() => { run(false) }, [run])
  useEffect(() => {
    if (!pollMs) return
    const t = setInterval(() => run(true), pollMs)
    return () => clearInterval(t)
  }, [pollMs, run])

  return { data, error, loading, reload, refresh }
}

export function fmtCountdown(seconds) {
  // !(x > 0) also catches NaN, which `<= 0` lets through and which rendered as
  // "NaN:NaN:NaN" whenever a match/league timestamp was missing.
  if (!(seconds > 0)) return '00:00'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return h > 0
    ? `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
    : `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}
