// Line-art icon set (24x24, stroke currentColor) for the v1-neon look.
const I = ({ children, size = 20, className = '', filled = false }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill={filled ? 'currentColor' : 'none'}
    stroke="currentColor"
    strokeWidth="1.8"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    {children}
  </svg>
)

export const IconUser = (p) => (
  <I {...p}><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 3.6-6 8-6s8 2 8 6" /></I>
)
export const IconBall = (p) => (
  <I {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7.5 8 10.4l1.5 4.6h5L16 10.4 12 7.5Z" />
    <path d="M12 3v4.5M8 10.4 3.6 9M9.5 15 6 19M14.5 15 18 19M16 10.4 20.4 9" />
  </I>
)
export const IconDumbbell = (p) => (
  <I {...p}>
    <path d="M6.5 6.5v11M17.5 6.5v11M3 9.5v5M21 9.5v5M6.5 12h11" />
  </I>
)
export const IconTrophy = (p) => (
  <I {...p}>
    <path d="M7 4h10v5a5 5 0 0 1-10 0V4Z" />
    <path d="M7 6H4a3 3 0 0 0 3 4M17 6h3a3 3 0 0 1-3 4M12 14v3M8.5 20h7M10 17h4v3h-4z" />
  </I>
)
export const IconStar = (p) => (
  <I {...p}><path d="m12 3 2.7 5.7 6.3.8-4.6 4.3 1.2 6.2L12 17l-5.6 3 1.2-6.2L3 9.5l6.3-.8L12 3Z" /></I>
)
export const IconCart = (p) => (
  <I {...p}>
    <path d="M3 4h2l2.5 12h11L21 8H6.1" />
    <circle cx="9.5" cy="19.5" r="1.4" /><circle cx="16.5" cy="19.5" r="1.4" />
  </I>
)
export const IconGear = (p) => (
  <I {...p}>
    <circle cx="12" cy="12" r="3.2" />
    <path d="M12 2.8v3M12 18.2v3M2.8 12h3M18.2 12h3M5.5 5.5l2.1 2.1M16.4 16.4l2.1 2.1M18.5 5.5l-2.1 2.1M7.6 16.4l-2.1 2.1" />
  </I>
)
export const IconBolt = (p) => (
  <I {...p} filled><path d="M13 2 4.5 13.5H11L9.5 22l8.5-11.5H12L13 2Z" stroke="none" /></I>
)
export const IconCoin = (p) => (
  <I {...p}>
    <circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="5.5" />
    <path d="M10.5 9.5h3.2M10.5 12h2.6M10.5 9.5V15" />
  </I>
)
export const IconChat = (p) => (
  <I {...p}><path d="M21 12a8 8 0 0 1-8 8c-1.5 0-3-.3-4.2-1L3 20l1.2-4.4A8 8 0 1 1 21 12Z" /></I>
)
export const IconCalendar = (p) => (
  <I {...p}>
    <rect x="3.5" y="5" width="17" height="15.5" rx="2.5" />
    <path d="M3.5 9.5h17M8 2.8V6M16 2.8V6" />
  </I>
)
export const IconBoot = (p) => (
  <I {...p}><path d="M4 16V5.5c0-.8.7-1.5 1.5-1.5h3c.8 0 1.5.7 1.5 1.5v5l7.6 3.4c1 .5 1.4 1 1.4 2.1v2H4v-2Z" /><path d="M7 18v2M11 18v2M15 18v2" /></I>
)
export const IconTarget = (p) => (
  <I {...p}><circle cx="12" cy="12" r="8.5" /><circle cx="12" cy="12" r="4.5" /><circle cx="12" cy="12" r="1" /></I>
)
export const IconShield = (p) => (
  <I {...p}><path d="M12 3 5 5.8v5.4c0 4.6 3 7.9 7 9.8 4-1.9 7-5.2 7-9.8V5.8L12 3Z" /></I>
)
export const IconRun = (p) => (
  <I {...p}>
    <circle cx="14.5" cy="5" r="2" />
    <path d="M9 20.5 11.5 15l-2-4 4-2.5 2.5 3.5 3.5.5M9.5 11 6 12.5l-2 3.5" />
  </I>
)
export const IconHeart = (p) => (
  <I {...p}><path d="M12 20.5S4 15 4 9.5A4.5 4.5 0 0 1 12 6.7a4.5 4.5 0 0 1 8 2.8c0 5.5-8 11-8 11Z" /><path d="M7 11h3l1-2 2 4 1-2h3" /></I>
)
export const IconChart = (p) => (
  <I {...p}><path d="M4 20V4M4 20h16M8 16v-5M12 16V8M16 16v-3M20 16V6" /></I>
)
export const IconPlus = (p) => (
  <I {...p}><path d="M12 5v14M5 12h14" /></I>
)
export const IconHome = (p) => (
  <I {...p}><path d="M3 11 12 4l9 7" /><path d="M5 10v10h5v-6h4v6h5V10" /></I>
)
export const IconGift = (p) => (
  <I {...p}><rect x="4" y="10" width="16" height="10" rx="1" /><path d="M4 10h16M12 10v10M12 10c-4 0-5-2-5-3.5A2 2 0 0 1 12 6a2 2 0 0 1 5 .5C17 8 16 10 12 10Z" /></I>
)
export const IconClose = (p) => (
  <I {...p}><path d="M6 6l12 12M18 6 6 18" /></I>
)
export const IconKey = (p) => (
  <I {...p}><circle cx="8" cy="15" r="4" /><path d="M11 12 20 3M16 7l3 3M13.5 9.5l2.5 2.5" /></I>
)
export const IconBox = (p) => (
  <I {...p}><path d="M3.5 8 12 3.5 20.5 8v8L12 20.5 3.5 16V8Z" /><path d="M3.5 8 12 12.5 20.5 8M12 12.5v8" /></I>
)
export const IconShirt = (p) => (
  <I {...p}><path d="m8.5 4-5 3 2 3.5 2-1V20h9v-10.5l2 1 2-3.5-5-3a3.5 3.5 0 0 1-7 0Z" /></I>
)
