import { useCallback, useEffect, useState } from 'react'

export function useApi(fn) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  const reload = useCallback(() => {
    setLoading(true)
    setError(null)
    fn()
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [fn])

  useEffect(() => { reload() }, [reload])
  return { data, error, loading, reload }
}

export function fmtCountdown(seconds) {
  if (seconds <= 0) return '00:00'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return h > 0
    ? `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
    : `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}
