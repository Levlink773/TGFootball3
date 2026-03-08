# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TG Football — a Telegram bot simulating a football player's career. Built with **aiogram 3.10** (async Telegram framework), **SQLAlchemy 2.0** (async ORM), **MySQL** (via aiomysql), and **aiohttp** (payment webhooks). All UI text is in Ukrainian.

## Commands

```bash
# Run the bot (starts both Telegram polling and aiohttp webhook server)
python main.py

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Install dependencies
pip install -r requirements.txt
```

## Architecture

### Entry Point

`main.py` runs two concurrent tasks via `asyncio.gather`:
- **Telegram bot polling** — aiogram dispatcher with registered routers
- **aiohttp web server** — handles Monobank payment webhooks and blitz proxy

`loader.py` initializes the `Bot`, `Dispatcher`, and `web.Application` instances. `load_utils.py` registers all routers and starts APScheduler jobs.

### Bot Layer (`bot/`)

Organized by feature domain, each with its own router:
- `routers/` — handler modules grouped by feature (character, club, league, gym, blitz, pvp_duels, training, stores, etc.)
- `keyboards/` — inline and reply keyboard builders
- `callbacks/` — CallbackData factories for inline buttons
- `states/` — aiogram FSM state groups
- `middlewares/` — request middleware (logging, auth)
- `filters/` — custom message filters

### Database (`database/`)

- `session.py` — async engine (`pool_size=10, max_overflow=0`) and `AsyncSession` factory
- `models/` — SQLAlchemy ORM models (UserBot, Character, Club, Item, Match, Training, Duel, Blitz, ClubInfrastructure, etc.)
- `model_base.py` / `base_acces.py` — declarative Base
- `events/` — SQLAlchemy event listeners for energy and experience changes

Alembic uses `pymysql` (sync) for migrations while the app uses `aiomysql` (async). The `alembic/env.py` reads DB credentials from `.env` to override `alembic.ini`.

### Game Modes

| Mode | Directory | Schedule |
|------|-----------|----------|
| Default League (9 tiers) | `league/` | Days 1-19 monthly, matches at 21:00 |
| Best Club League | `best_club_league/` | Days 1-10 |
| Top 20 Power League | `league_20_power_club/` | Days 1-10 |
| New Clubs League | `new_clubs_league/` | Days 12-25 |
| Blitz tournaments | `blitz/` | Daily at 15:00 and 19:00 |
| PvP Duels | `pvp_duels/` | On-demand |

League registration happens on days 20-31 of each month.

### Services (`services/`)

Business logic layer. Key service pattern: `league_services/` uses a `base_service.py` abstract base class with concrete implementations for each league type.

### Schedulers (`schedulers/`)

APScheduler async jobs for: energy resets, gym task resets, education center rewards (12h cycle), training sessions, VIP pass expiration, season endings, ranking recalculation, match start notifications.

### Payments (`webhook_api/`, `api/`)

Monobank webhook handlers in `webhook_api/` for: energy, boxes, money, VIP passes, position changes, training keys. Payment invoice creation via `api/` module.

### Match Simulation (`match/`)

Match engine with stat-based calculations. Position coefficients defined in `config.py` (`POSITION_COEFFICIENTS`) affect character performance.

## Key Configuration

- `config.py` — enums (Gender, PositionCharacter), league tiers, position stat coefficients, admin IDs, game constants
- `constants.py` / `constants_leagues.py` — game balance constants and league-specific rules
- `.env` — DB credentials, BOT_TOKEN, Monobank token, webhook URLs (see `.env.example`)

## Rules

Path-scoped rules in `.claude/rules/` provide detailed guidance when working in specific areas:

- `database.md` — async/sync driver split, session usage, migration gotchas (loaded for `database/`, `alembic/`, `services/`)
- `bot.md` — router registration, singletons, Ukrainian text (loaded for `bot/`, `loader.py`, `load_utils.py`)
- `python-compat.md` — Python 3.13 breaking changes (always loaded)
- `game-logic.md` — position coefficients, calendar scheduling, league inheritance (loaded for `match/`, `league/`, `blitz/`, etc.)
- `payments.md` — webhook handler registration, Monobank setup (loaded for `webhook_api/`, `api/`, `main.py`)

## Deployment

Systemd service + Nginx reverse proxy with SSL (Certbot). See `deploy/DEPLOY.md` for full setup on Ubuntu 22.04+.
