---
paths:
  - "match/**"
  - "league/**"
  - "blitz/**"
  - "pvp_duels/**"
  - "best_club_league/**"
  - "league_20_power_club/**"
  - "new_clubs_league/**"
  - "config.py"
  - "constants.py"
  - "constants_leagues.py"
---

# Game Logic Rules

- Character stats are modified by `POSITION_COEFFICIENTS` in `config.py` — changes there affect all match outcomes.
- League schedule is calendar-driven: matches days 1-19, registration days 20-31. Do not change this without understanding all scheduler dependencies in `schedulers/`.
- Blitz runs at fixed times (15:00, 19:00 daily). Configuration is coupled between `blitz/` logic and scheduler setup in `load_utils.py`.
- League services follow an inheritance pattern: `base_service.py` → concrete implementations (`league_service.py`, `best_club_league.py`, etc.). New league types must extend `base_service.py`.
