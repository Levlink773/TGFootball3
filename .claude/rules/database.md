---
paths:
  - "database/**"
  - "alembic/**"
  - "services/**"
---

# Database Rules

- App uses `aiomysql` (async). Alembic uses `pymysql` (sync). Never mix them.
- All DB operations must go through `async_session` from `database/session.py`. Never create engines directly.
- Models inherit from `Base` in `database/model_base.py`. All models must be imported in `database/base_acces.py` for Alembic autogenerate to detect them.
- MySQL TIMESTAMP columns cannot have default `0000-00-00 00:00:00` — use `'2000-01-01 00:00:00'` instead.
- On a fresh database, use `Base.metadata.create_all` (called in `loader.py`), then `alembic stamp head` to sync migration state. Alembic migrations have ordering issues on empty DBs.
- `expire_on_commit=False` is set on the session factory — objects remain usable after commit without re-fetching.
