"""Startup schema-drift guard.

Defense-in-depth against DB schema lagging the code. The real fix is the deploy
script running `alembic upgrade head` before every restart; this just shouts in
the log if a boot ever comes up with the DB behind the latest migration head, so
drift is caught immediately instead of surfacing as a random runtime crash later.

Deliberately log-only and fully non-fatal: it must NEVER raise or make a network
call at startup (a Telegram call here would risk crashing the boot on the VPS's
flaky network — see FUTURE_IMPROVEMENTS #4).
"""
import os

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text

from database.session import engine
from logging_config import logger

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


async def check_schema_at_head() -> bool:
    """Return True if the DB is at the latest alembic head, False on drift.

    Any internal error is swallowed (returns True) so the guard can never block
    startup — it is a canary, not a gate.
    """
    try:
        cfg = Config(os.path.join(_BASE_DIR, "alembic.ini"))
        cfg.set_main_option("script_location", os.path.join(_BASE_DIR, "alembic"))
        heads = set(ScriptDirectory.from_config(cfg).get_heads())

        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            db_revs = {row[0] for row in result.fetchall()}

        if db_revs == heads:
            logger.info("schema_guard: DB schema at head %s", sorted(heads))
            return True

        logger.critical(
            "schema_guard: DB SCHEMA DRIFT detected — db=%s expected head=%s. "
            "Apply migrations with `alembic upgrade head` "
            "(deploy/restart_server.sh does this automatically).",
            sorted(db_revs) or "{}",
            sorted(heads),
        )
        return False
    except Exception as exc:  # noqa: BLE001 - never block startup on the guard
        logger.warning("schema_guard: could not verify schema (%s)", exc)
        return True
