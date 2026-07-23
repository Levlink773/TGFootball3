const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:3004'

// initData from Telegram WebApp SDK; dev fallback = ?initData=<forged> query param
function initData() {
  const tg = window.Telegram?.WebApp
  if (tg?.initData) return tg.initData
  return new URLSearchParams(window.location.search).get('initData') || ''
}

const HTTP_MESSAGES = {
  401: 'Сесія недійсна — відкрий гру через кнопку в Telegram.',
  403: 'Доступ заборонено.',
  404: 'Дані не знайдено.',
  500: 'Помилка сервера. Спробуй ще раз за хвилину.',
}

export async function api(path, options = {}) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 20000)
  let res
  try {
    res = await fetch(`${API_URL}/api${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        Authorization: `tma ${initData()}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })
  } catch {
    throw new Error("Немає з'єднання. Перевір інтернет і спробуй ще раз.")
  } finally {
    clearTimeout(timer)
  }
  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err = new Error(body.detail || HTTP_MESSAGES[res.status] || `Помилка ${res.status}`)
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
export const startTraining = (stat, minutes) =>
  api('/training/start', { method: 'POST', body: JSON.stringify({ stat, minutes }) })
export const claimEducation = () => api('/education/claim', { method: 'POST' })
export const getTrainerSession = () => api('/trainer/session')
export const trainerJoin = () => api('/trainer/join', { method: 'POST' })
export const trainerAnswer = (direction) =>
  api('/trainer/answer', { method: 'POST', body: JSON.stringify({ direction }) })
export const trainerPickStat = (stat) =>
  api('/trainer/pick-stat', { method: 'POST', body: JSON.stringify({ stat }) })
export const getTeam = () => api('/team')
export const getJoinList = () => api('/team/join-list')
export const joinClub = (club_id) =>
  api('/team/join', { method: 'POST', body: JSON.stringify({ club_id }) })
export const leaveClub = () => api('/team/leave', { method: 'POST' })
export const getStatistics = () => api('/statistics')
export const getTutorial = () => api('/tutorial')
export const completeTutorial = () => api('/tutorial/complete', { method: 'POST' })
export const getInventory = () => api('/inventory')
export const equipItem = (item_id) =>
  api('/inventory/equip', { method: 'POST', body: JSON.stringify({ item_id }) })
export const unequipItem = (category) =>
  api('/inventory/unequip', { method: 'POST', body: JSON.stringify({ category }) })
export const sellItem = (item_id) =>
  api('/inventory/sell', { method: 'POST', body: JSON.stringify({ item_id }) })
export const kickMember = (user_id) =>
  api('/team/kick', { method: 'POST', body: JSON.stringify({ user_id }) })
export const transferOwner = (user_id) =>
  api('/team/transfer', { method: 'POST', body: JSON.stringify({ user_id }) })
export const renameClub = (name) =>
  api('/team/rename', { method: 'POST', body: JSON.stringify({ name }) })
export const setInviteOnly = (enabled) =>
  api('/team/invite-only', { method: 'POST', body: JSON.stringify({ enabled }) })
export const setClubDescription = (text) =>
  api('/team/description', { method: 'POST', body: JSON.stringify({ text }) })
export const upgradeInfrastructure = (type) =>
  api('/team/infrastructure/upgrade', { method: 'POST', body: JSON.stringify({ type }) })
export const getQuests = () => api('/quests')
export const claimQuests = (key) => api('/quests/claim', { method: 'POST', body: JSON.stringify({ key }) })
export const claimGift = () => api('/gift/claim', { method: 'POST' })
export const claimQuestBonus = () => api('/quests/claim-bonus', { method: 'POST' })
export const getSettings = () => api('/settings')
export const updateSettings = (bot_buttons_enabled) =>
  api('/settings', { method: 'POST', body: JSON.stringify({ bot_buttons_enabled }) })

// Open a Monobank invoice URL outside the webview
export function openInvoice(url) {
  const tg = window.Telegram?.WebApp
  if (tg?.openLink) tg.openLink(url)
  else window.open(url, '_blank')
}
