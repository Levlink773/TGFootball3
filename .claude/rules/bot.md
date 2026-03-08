---
paths:
  - "bot/**"
  - "loader.py"
  - "load_utils.py"
---

# Bot Rules

- All routers must be registered in `load_utils.py` via `dp.include_router()`. Adding a router file alone does nothing.
- Use `loader.bot` and `loader.dp` singletons — never instantiate new Bot or Dispatcher objects.
- All user-facing text must be in Ukrainian.
- Keyboards go in `bot/keyboards/`, callback data factories in `bot/callbacks/`, FSM states in `bot/states/`.
- Admin-only handlers should check against `ADMINS` list from `config.py`.
