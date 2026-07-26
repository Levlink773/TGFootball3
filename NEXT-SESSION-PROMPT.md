# TG Football Mini App — go-live session (после приёмки на тестовом боте)

## Project
Client: Maxim. Game: @tg_football_game_bot (prod) / @testbottgfootball_bot (test).
KP (kp.html): TG Football 9 500 + Questaria 6 500 = 16 000 грн.
Payments: 3 000 старт PAID + 1 000 аванс PAID → remaining 5 500 сдача TG Football.
Blocks: 1 Фундамент ✅ · 2 Mini App ✅ DEPLOYED (test-bot phase) · 3 Движок (not started).

## Deployed state (as of 2026-07-22)
- App LIVE: https://app.football-blitz.online (cert Let's Encrypt, vhost tgfootball-app.conf,
  nginx → static /root/footballgame/webapp/dist + /api/ → uvicorn :3004).
- Services on VPS (root@46.202.190.222, key ~/.ssh/footballblitz_vps):
  footballgame (prod bot, NOT touched), footballgame-api (uvicorn :3004),
  tgfootball-testbot (polling stub, /start → webapp button), footballblitz (sibling, DON'T touch).
- Prod .env has WEBAPP_ORIGIN + TEST_BOT_TOKEN. auth.py accepts both bot tokens (commit 4fa8c8f).
- Migration a1b2c3d4e5f6 applied: users.bot_buttons_enabled tinyint(1) default 1.
- All API endpoints verified 200 with forged auth vs prod data; 401 without.
- Verified test-token initData validates. Backups of .env: /root/.env.bak-20260721, .env.bak-20260721-2.
- Dev repo: ~/Personal/projects/tg-football/test (branch prod-snapshot).
  Moved here by the 2026-07-26 home reorg; the old ~/dev/tg-football-test path is GONE.
  NEVER work in the iCloud "football_game 3" copy.
- Deploy gotchas learned: macOS tar ships ._AppleDouble files (use COPYFILE_DISABLE=1 tar);
  Cyrillic migration filenames NFC/NFD duplicate on linux — check `alembic heads` after any sync.

## Session goals (in order)

### 1. Phone checklist results (from Maxim / own phones via @testbottgfootball_bot)
All 5 tabs live data · match/blitz registration · shop coin buy · Monobank invoice opens
(real pay of энергия 100 грн only with Maxim confirm) · settings toggle persists ·
tutorial once (localStorage tgf_tutorial_done) · chat icon → t.me/tgfootballchat ·
safe-area top inset in TG webview · no CORS/401. Fix whatever checklist surfaces.

### 2. Go-live on prod bot (ONLY after checklist green + Maxim's «ок»)
- BotFather → @tg_football_game_bot → Bot Settings → Menu Button → URL = https://app.football-blitz.online
  (user does in Telegram; Main App enable optional).
- Optionally announce in game chat (Maxim decides wording).
- After go-live: stop test stub — `systemctl disable --now tgfootball-testbot` (keep unit file).

### 3. Milestone: сдача TG Football
- Payment 5 500 грн trigger (3 000 + 1 000 already paid).
- Update KP status (client-delivery/tg-football-concept-2026-07-17/05-kp/kp.html) → «сдано»,
  payment card СДАЧА → ✅.

### 4. Block 2 leftover (small, quiet window)
- Wire users.bot_buttons_enabled into prod bot: where reply keyboards sent, skip if flag false
  (grep reply_markup in bot/, central helper if exists). Deploy = bot restart via restart_server.sh
  (runs alembic + restart) — do in quiet window, NOT during blitz (prod schedule 15:00, 19:00 Kyiv).

### 5. Next block: Движок (block 3) — separate KP scope
Живой матч: new simulation (donate-to-goal), engine exposes data → app polls/streams. Not this session
unless explicitly asked.

## Rules
- Commit in ~/Personal/projects/tg-football/test, conventional commits, no AI attribution.
- PROD IS SOURCE OF TRUTH. Backup any VPS file before editing (cp X X.bak-YYYYMMDD).
- Never cache balances/energy. initData validation on EVERY endpoint.
- Don't restart footballgame service except step 4, quiet window only.
- rsync may be blocked by permission classifier → use COPYFILE_DISABLE=1 tar + scp + extract.
