# TG Football — Mini App

Telegram Mini App for the TG Football career game (client: Maxim). Ukrainian-language.
Replaces the bot's chat-button UI: everything playable happens inside the app.

- **Register:** product (app UI; users are in a task: train, register for matches, buy gear)
- **Users:** Telegram players of @tg_football_game_bot, on phones, dark Telegram theme, one-handed use
- **Frame:** max-w 422px phone frame, bottom tab nav (Гравець · Матчі · Трен-ня · Ліга · Зал Слави) + header (balance, shop, settings)
- **Design system:** locked client-approved "V1 neon" — dark navy `#0a0e14` bg, gold `#ffd700` + cyan `#00ffff` accents, Ukrainian display font styling (h-display class), glow rings. Reference frames: client-delivery/tg-football-concept-2026-07-17/02-frames/v1-neon_*.png. Identity preservation wins over new palettes.
- **Art:** 65 generated webp assets in webapp/src/assets/art (manifest index.js: art/gearArt/clubCrest/avatarArt)
- **Stack:** React 18 + Vite + Tailwind (utility classes, tokens in index.css), FastAPI sidecar (webapp_api, port 3004), initData auth on every endpoint, MySQL shared with the bot
- **Payments:** Monobank invoices (real money) — never cache balances; invoice opens externally
- **Screens:** Home, Player, Matches, Training, League, HallOfFame, Shop, Settings (+ planned: Team, Statistics, QTE trainer)
- **Non-negotiables:** initData validation server-side, no destructive writes without bot-logic parity, Ukrainian copy, safe-area insets in TG webview
