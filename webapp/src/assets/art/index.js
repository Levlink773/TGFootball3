// Art manifest — all generated V1-neon assets, keyed by filename (no extension).
// import.meta.glob keeps the build green even while some files are missing.
const files = import.meta.glob('./*.webp', { eager: true, import: 'default' })

export const art = Object.fromEntries(
  Object.entries(files).map(([path, url]) => [path.slice(2).replace(/\.webp$/, ''), url])
)

// Deterministic crest for procedurally-named clubs: same name -> same crest.
const CREST_COUNT = 12
export function clubCrest(name) {
  if (!name) return null
  let h = 0
  for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) >>> 0
  return art[`crest-${String((h % CREST_COUNT) + 1).padStart(2, '0')}`] || null
}

// Gear item name -> set art key (matched by set keyword in the item name).
const SET_KEYS = [
  ['Домінанта', 'luxe-dominanta'],
  ['Елітного Гравця', 'luxe-elitnogo-gravtsia'],
  ['Легенда Ліги', 'luxe-legenda-ligy'],
  ['початківця', 'set-pochatkivtsia'],
  ['Дзідана', 'set-dzidana'],
  ['Базов', 'set-bazova'],
  ['Тренувальн', 'set-trenuvalna'],
  ['молодого таланта', 'set-molodogo-talanta'],
  ['юніора', 'set-yuniora'],
  ['аматора', 'set-amatora'],
  ['майбутньої зірки', 'set-maybutnoi-zirky'],
  ['професіонала', 'set-profesionala'],
  ['майстра поля', 'set-maistra-polia'],
  ['Легенди Арени', 'set-legendy-areny'],
  ['Короля Поля', 'set-korolia-polia'],
  ['Воїн Поля', 'set-voin-polia'],
  ['Футбольний Гранд', 'set-futbolnyi-grand'],
]
export function gearArt(itemName) {
  const hit = SET_KEYS.find(([kw]) => itemName.includes(kw))
  return hit ? art[hit[1]] || null : null
}

// Player avatar by gender + position (API values).
const POS_SLUG = {
  'Нападник': 'attacker',
  'Півзахисник': 'midfielder',
  'Захисник': 'defender',
  'Воротар': 'goalkeeper',
}
export function avatarArt(gender, position) {
  // The API returns Gender.value ("Чоловік"/"Жінка"), never the member name, so
  // matching on "WOMAN" alone made every woman avatar unreachable. Both forms are
  // accepted because the wizard posts member names.
  const g = /жін|woman/i.test(String(gender || '')) ? 'woman' : 'man'
  const p = POS_SLUG[position]
  return p ? art[`avatar-${g}-${p}`] || null : null
}
