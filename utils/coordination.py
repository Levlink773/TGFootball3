"""Coordination primitive — the 'one actor' boundary.

Why this exists: the bot had no guard against a second instance (botched restart, a stray
dev/server run, a duplicate deploy) running the same schedulers. Each running copy fires its
OWN training / education / blitz reminders, so every reminder was delivered once PER process —
that is the duplicate-broadcast spam the client saw.

single_instance_lock() takes a host-level flock; a second process on the same host refuses to
start. It FAILS OPEN: a lock-file quirk must never take the live bot down.

Note: the lock is per-host. It stops same-host duplicates. Running the bot on two different
hosts at once can only be prevented by deploying it in exactly one place (or rotating the bot
token so stale instances lose access).
"""
import os
import socket
import fcntl

try:
    from logging_config import logger
except Exception:  # never let the logging subsystem block the single-instance guard
    import logging
    logger = logging.getLogger(__name__)

_LOCK_PATH = "/tmp/tgfootball.lock"
_lock_fh = None  # module-global: keep the fd alive for the whole process, or the lock releases
_INSTANCE_ID = f"{socket.gethostname()}:{os.getpid()}"


def single_instance_lock() -> bool:
    """Acquire an exclusive host lock. Returns False ONLY if another TG Football process on
    this host already holds it (caller should exit). Any other error -> True (don't let a
    lock-file quirk block startup)."""
    global _lock_fh
    try:
        _lock_fh = open(_LOCK_PATH, "w")
        fcntl.flock(_lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _lock_fh.write(_INSTANCE_ID)
        _lock_fh.flush()
        logger.info("Single-instance lock acquired (%s).", _INSTANCE_ID)
        return True
    except BlockingIOError:
        logger.error(
            "Another TG Football process already holds %s - refusing to start a duplicate. "
            "This is the guard against doubled broadcasts.", _LOCK_PATH
        )
        return False
    except Exception as e:  # noqa: BLE001 - lock is best-effort, never block startup on it
        logger.warning("single_instance_lock unexpected error (%s); proceeding without host lock.", e)
        return True
