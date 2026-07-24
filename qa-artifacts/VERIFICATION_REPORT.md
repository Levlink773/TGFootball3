# TG Football Mini App — verification report

- **Project:** TG Football (`@tg_football_game_bot`), Telegram Mini App, client Maxim
- **Repo/branch:** `~/dev/tg-football-test` @ `prod-snapshot`
- **Baseline audited:** `ce5d738` · **Fixes:** `aff5130`, `c3e1ad3`
- **Date:** 2026-07-25
- **Live app:** https://app.football-blitz.online (nginx static + `/api/` → uvicorn :3004)
- **Scope note:** FootballBlitz is a *separate* sibling project (repo `alotofms/FootballBlitz`,
  DB `football_blitz`, unit `footballblitz`). It shares the VPS and the domain name only.
  Nothing in this audit read or wrote it.

## Environment attestation

All destructive testing ran against a **local** MySQL (`DB_HOST=localhost`, DB `tg_football`,
alembic head `f6a7b8c1d2e3`, 58 users / 58 characters / 58 clubs) and a local API on
`127.0.0.1:3004`. Production was touched **read-only**, and only to fetch the public JS bundle
and its headers.

One incident worth recording: an orphaned `vite preview --strictPort 5173` from a previous
session was serving a production build against the production API. Nine `GET` requests for a
nonexistent user (`999000111`) reached prod and returned 404 before this was spotted and the
process killed. No writes, no state change. Local dev was then pinned to `:5173` with
`--strictPort` so port drift cannot silently repoint the harness again.

DB restored to exact baseline after testing: `58 / 58 / 58`, character 6 money `10000`,
energy `150`, zero test residue. Replayable dump at
`<scratchpad>/db/baseline-replayable.sql` (the first dump carried `GTID_PURGED` statements and
would **not** replay — re-taken with `--set-gtid-purged=OFF`).

## Static gate

| Check | Result |
|---|---|
| `npm run lint` (oxlint) | **0 errors, 0 warnings** (was 0 errors / 2 warnings) |
| `python -m compileall` over api, webhook, services, bot | clean, exit 0 |
| `alembic heads` | single head `f6a7b8c1d2e3` — no fork |
| Route registration | 41 routes |
| `pytest tests/` | **26 passed, 1 skipped** |

The skip is the `TEST_BOT_TOKEN` impersonation exploit, which only runs when the API is
deliberately started with that token set. It was executed manually — see F1.

## Findings

Nine defects were reproduced by exploit **before** any fix, then closed. Severity is mine.

| # | Sev | Defect | Proof on `ce5d738` | Status |
|---|-----|--------|--------------------|--------|
| F2 | HIGH | Monobank signature verification returned `True` when `TOKEN_MONOBANK` was unset — a forged callback to a guessed `invoiceId` credits real coins | `verify(None, body)` → `True` | **FIXED** — fails closed |
| F1 | HIGH | `TEST_BOT_TOKEN` was a permanent second initData signer: sign as any victim, get authenticated as them | signed as victim `29015796` with a fake token → **HTTP 200**, returned their name and balance 920; clean API → 401 | **FIXED** — opt-in behind `ALLOW_TEST_BOT_INITDATA=1`; still 401 with the token present |
| F6 | HIGH | Webhook replay double-credit: `status` was read, then credited, then set | 2 concurrent identical callbacks → balance moved **1000**, expected 500 | **FIXED** — `claim_payment()` makes the status flip the atomic gate |
| F3 | HIGH | `merge()` of a **detached** row rewrote the whole loaded graph from a stale snapshot | unequip reverted a concurrent credit: **10777 → 10000**; `transfer_club_owner` reverted `energy_applied` 500 → 0 | **FIXED** — targeted single-column `UPDATE` |
| F4 | HIGH | `/api/trainer/pick-stat` set `stat_claimed` *after* an `await` | 20 concurrent requests → reward awarded **20×** | **FIXED** — claim before first await |
| F9 | MED | `edit_character_energy` uncapped, `consume_energy` unfloored, both lost updates | energy reached **650** (cap 300) and **−989** | **FIXED** — `SELECT FOR UPDATE` + clamp to 150/300 |
| F8 | MED | `remove_training_key` decremented unconditionally | 5 concurrent joins on 1 key → `training_key = **−4**` | **FIXED** — conditional debit + rowcount gate; caller spends key first |
| F7 | MED | Club rename/description accepted `<` `>`; the bot renders them with `parse_mode=HTML` into league broadcasts | stored `<a href='https://evil'>ФК` verbatim | **FIXED** — rejected at the API boundary (400) |
| F11 | LOW | `getattr(cls, club.schema)` on an unvalidated `String(255)` | a crafted schema broke match registration for the whole club | **FIXED** — derived whitelist + logged fallback |
| F13 | LOW | Payment webhook returned raw exception text; a `ValidationError` object was handed to `json_response` | body contained `secret-internal-detail-xyz` | **FIXED** — generic message, detail to log only |
| F5 | HIGH | **No rate limiting anywhere**; DB pool is 10+20 and every service call opens its own session | — | **MITIGATED, NOT YET LIVE** — nginx `limit_req` written; needs the operator to add three `limit_*_zone` lines to `http{}` and reload |
| F12 | LOW | `?initData=` dev fallback shipped in the production bundle — a 24 h bearer credential in the URL | present in the live bundle | **FIXED** — behind `import.meta.env.DEV`, verified stripped from the new build; deploy script now refuses a bundle containing it |
| F14 | LOW | `requirements.txt` missing `fastapi`/`uvicorn` although the API runs uvicorn | — | **FIXED** — pinned to installed versions |

### Rejected as false positives (verified against real code, not fixed)

- `equip_item`, `update_character_club_id`, `update_character_education_time` call
  `session.add()` **before** `merge()`, which re-attaches the instance so only changed
  columns are written. Emitted SQL confirmed to be a single-column UPDATE. Not clobbering.
- `League.jsx:18`, `Training.jsx:148`, `Home.jsx:248` cannot dereference undefined — the
  backend returns module-level constant dicts (4 leagues, 2 blitz slots, unconditional
  `trainer` key).
- A proposed "fix" to convert the energy/exp helpers to Core `update()` would have **broken
  production**: it bypasses the `Character` `before_update` listener that drives the
  low-energy upsell, the 300-energy referral reward and the new-member box. Used a row lock
  instead.

## Auth matrix (all against `/api/player`)

| Case | Result |
|---|---|
| valid initData | 200 |
| no header · empty scheme · `Bearer` scheme · garbage · foreign-token signature · 25 h-old `auth_date` · tampered hash · no `user` field | **401 ×8** |
| brand-new user (no character) | 404 `{"detail":"No character"}` — clean, no stack trace |
| `/api/health` | 200, open by design |

Ownership guards for inventory and team operations were read and are enforced server-side
(`owner_character_id` scoping, `_owner_club` 403). No IDOR found.

## The black screen Maxim reported

Maxim, 2026-07-24 13:18: a friend with no account opened the app and got a black screen that
never loaded. **This is already fixed and live**, and it was not a missing screen:

- The onboarding screen ("Ласкаво просимо! У тебе ще немає футболіста…" with a button back to
  the bot) has existed since `6ba90d5`, **2026-07-22 13:35**.
- The live bundle `index-BNxkxJHh.js` carries it, and a new-user load against production
  rendered it correctly.
- The live bundle's `Last-Modified` is **2026-07-24 15:35 UTC = 18:35 Kyiv** — redeployed
  ~5 hours *after* his test, by `ce5d738` "atomic webapp deploy, no black-screen window
  during updates".

Root cause was the old non-atomic deploy: it removed hashed assets while Telegram's webview
still held a cached `index.html` pointing at them, so the app fetched a 404'd bundle and
rendered nothing. `ce5d738` keeps old assets, closing that window.

Verified locally on the fixed build: a forged initData for a user with no `users`/`characters`
row renders onboarding, and the gate holds when tabs are clicked rather than falling through
to a broken screen.

## Browser pass — 11 screens, iPhone viewport 375×812

Home · Player · Matches · Training · League · Hall of Fame · Shop · Settings · Team ·
Statistics · Trainer — all render with live data from the local API. Screenshots
`00-newuser-onboarding.png` … `11-trainer.png`.

Throughout the pass the only console error is the Telegram SDK's own
`Method showPopup is not supported in version 6.0`, logged by the SDK outside Telegram. It no
longer throws — the call is now wrapped. Home shows balance `10 000`, energy `150/150`,
tournament countdowns render as `7д 07:13:41` (no `NaN`).

Mutation exercised end to end: **daily gift claim** → money `10000 → 10020`, energy correctly
held at the `150` cap by the new clamp. No 500s and no tracebacks in the uvicorn log for the
entire session; the only non-2xx entries are this audit's own 401/404/400 probes.

## PRODUCTION CONFIG CHECK (read-only, 2026-07-25)

Checked `/root/footballgame/.env` and the loaded `config` on the VPS. Presence and SHA-256
prefixes only — no secret values were read or printed.

| Key | Prod state | Consequence |
|---|---|---|
| `TOKEN_MONOBANK` | **LOADED**, len 23, sha `2bbd1f5c0b17` | Signature verification **is active** in production. The fail-closed fix is therefore safe to ship. |
| `TEST_BOT_TOKEN` | **SET (len 46)** | With the pre-fix `auth.py`, the test-bot token is a live second signer → **anyone holding it can authenticate as ANY player**. Still open until Unit B ships and the var is removed. |
| `ALLOW_TEST_BOT_INITDATA` | absent | correct — the new opt-in flag is off |
| services | `footballgame`, `footballgame-api`, `tgfootball-testbot` all active | test bot still running |
| `limit_req_zone` in nginx.conf | **0** | no rate limiting in force |
| prod alembic head | `f6a7b8c1d2e3` | matches local — no migration drift |

> **Correction to an earlier draft of this report.** It stated that `TOKEN_MONOBANK` was
> absent on production and that Monobank signature verification was consequently off. That
> was wrong. The prod `.env` writes the key as `TOKEN_MONOBANK =` (space before `=`), which
> the first `grep -E '^TOKEN_MONOBANK='` did not match; python-dotenv strips the whitespace
> and loads it correctly. Confirmed by importing `config` on the VPS: the token is loaded,
> length 23. **Signature verification has been on the whole time**, and the fail-closed fix
> does not risk stopping payments.

The token is the same one used by the sibling FootballBlitz project
(`~/.claude/env/footballblitz.env`, identical sha `2bbd1f5c0b17`) — i.e. one Monobank
merchant serves both games, so no token change is required.

## Payment atomicity (commit `c3e1ad3`)

The first fix made the replay gate atomic but left claim and credit in **separate**
transactions. A crash between them would mark a payment paid with nothing delivered, and
Monobank's retry would then see `status=True` and credit nothing.

`PaymentServise.claim_and_apply(order_id, *stmts)` now runs the `status False->True` gate and
the credit in **one** transaction — both commit or both roll back. Applied to money, energy,
training key, change-position and VIP pass. Two credits are computed in SQL so a stale read
cannot skew them: energy uses `LEAST(cap, current + amount)`, VIP uses
`DATE_ADD(GREATEST(NOW(), COALESCE(expiry, NOW())), INTERVAL n DAY)` (extending an active
pass rather than truncating it; `n` comes from the server-side catalog, never the callback).

Box is the exception and is documented as such: its grant is an animated Telegram flow with
sleeps plus three separate credits, so it cannot join a DB transaction. It keeps claim-first
(at-most-once — a replay must never hand out a second box) and now logs
`PAID BUT BOX NOT DELIVERED` if the delayed open throws, so it is reconcilable by hand.

Proven by two new tests: a failing credit leaves `status=0` and the balance untouched, and 20
concurrent deliveries produce exactly one winner and one credit.

## Residual risk / not done

1. **F5 rate limiting is not live.** The vhost is updated but the three `limit_*_zone`
   directives must be added to `http{}` in `/etc/nginx/nginx.conf` on the VPS, then
   `nginx -t && systemctl reload nginx`. Until then the API has no throttle.
2. **`TEST_BOT_TOKEN` must be removed from the production `.env`.** The code now ignores it
   without the opt-in flag, but removing it eliminates the credential entirely.
3. **`TOKEN_MONOBANK` must be non-empty on the VPS before Unit C ships.** F2 now fails
   closed, so a blank token would stop crediting all payments instead of accepting forgeries.
4. Formation cap and the 11-member club cap remain read-then-write. Exploiting either needs a
   sub-100 ms collision exactly at the cap, no money is involved, and the atomic form hits
   MySQL error 1093. Deferred deliberately.
5. `/api/team` still 500s on a member row with an invalid `position` enum. No user-reachable
   path writes one; it came from a UTF-8 mangling incident in test setup.
6. Reward/tuning numbers (quest energy 20/30/25, 50-coin bonus, gift 10–50) are still
   placeholders awaiting Maxim's sign-off.
7. Energy above the tier cap is now clamped. If Maxim intends overflow, the display should be
   fixed instead of the clamp — his call.

## Deployment plan (not yet executed)

| Unit | Contents | Restart |
|---|---|---|
| 0 | nginx rate limits | `nginx -t && systemctl reload nginx` |
| A | frontend bundle | `deploy/deploy_webapp.sh`, atomic, none |
| B | `webapp_api` (auth, trainer, team) | `systemctl restart footballgame-api`, sub-second |
| C | shared `services/` + `webhook_api` + handlers | `deploy/restart_server.sh` — **quiet window only**, prod blitz runs 15:00 and 19:00 Kyiv |
| D | migrations | none required |

Prod DB reset (client-authorised) is sequenced **last**, after a fresh Telegram account
completes registration on production — because wiping `users` makes every player a new user,
which is exactly the path that produced the black screen.

## Verdict

Every defect proven by exploit in this audit is fixed, with a committed regression test that
fails on `ce5d738` and passes on `aff5130`. Static gate is green, the suite is green, the
11-screen browser pass is clean, and the local DB is byte-identical to its baseline.

The one item that is written but **not yet in force** is the rate limiter (F5), which needs an
operator step on the VPS.
