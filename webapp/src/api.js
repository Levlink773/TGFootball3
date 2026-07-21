const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:3004'

// initData from Telegram WebApp SDK; dev fallback = ?initData=<forged> query param
function initData() {
  const tg = window.Telegram?.WebApp
  if (tg?.initData) return tg.initData
  return new URLSearchParams(window.location.search).get('initData') || ''
}

export async function api(path, options = {}) {
  const res = await fetch(`${API_URL}/api${path}`, {
    ...options,
    headers: {
      Authorization: `tma ${initData()}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err = new Error(body.detail || `HTTP ${res.status}`)
    err.status = res.status
    throw err
  }
  return body
}

export const getPlayer = () => api('/player')
export const getMatches = () => api('/matches')
export const getLeagues = () => api('/leagues')
export const getHallOfFame = () => api('/hall-of-fame')
export const getTraining = () => api('/training')
export const getShop = () => api('/shop')
export const registerMatch = (matchId) =>
  api('/match/register', { method: 'POST', body: JSON.stringify({ match_id: matchId }) })
export const registerBlitz = () => api('/blitz/register', { method: 'POST' })
export const createInvoice = (product_type, product_key) =>
  api('/shop/invoice', { method: 'POST', body: JSON.stringify({ product_type, product_key }) })
export const buyItem = (item_id, luxe = false) =>
  api('/shop/buy-item', { method: 'POST', body: JSON.stringify({ item_id, luxe }) })
export const getSettings = () => api('/settings')
export const updateSettings = (bot_buttons_enabled) =>
  api('/settings', { method: 'POST', body: JSON.stringify({ bot_buttons_enabled }) })

// Open a Monobank invoice URL outside the webview
export function openInvoice(url) {
  const tg = window.Telegram?.WebApp
  if (tg?.openLink) tg.openLink(url)
  else window.open(url, '_blank')
}
