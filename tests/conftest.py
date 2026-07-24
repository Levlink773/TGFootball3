"""Shared fixtures for the TG Football audit suite.

Everything here talks to the LOCAL stack only: MySQL on localhost (DB_HOST in .env)
and the API on 127.0.0.1:3004. Nothing in this package may reach the production VPS.
"""
import hashlib
import hmac
import json
import os
import subprocess
import time
import urllib.parse

import pytest

os.environ.setdefault("PYTEST_RUNNING", "1")

import config  # noqa: E402  (loads .env)

# Importing the app registers EVERY ORM model (its routers import them all), so
# cross-model relationships like Character->Club resolve in-process.
import webapp_api.app  # noqa: E402,F401

API = os.getenv("QA_API_URL", "http://127.0.0.1:3004")

# A real character in the local DB with coins + energy, and owner of its club.
QA_UID = int(os.getenv("QA_UID", "3312785"))
# A second real character, used as the victim in the IDOR matrix.
QA_UID_B = int(os.getenv("QA_UID_B", "29015796"))
# No users/characters row exists for this id.
QA_UID_ABSENT = int(os.getenv("QA_UID_ABSENT", "999000111"))


def forge(uid: int, token: str | None = None, age_s: int = 0, first: str = "Dev") -> str:
    """Build a Telegram initData string signed exactly the way auth.py verifies it."""
    token = token or config.BOT_TOKEN
    user = json.dumps(
        {"id": uid, "first_name": first, "username": "dev_local", "language_code": "uk"},
        separators=(",", ":"),
    )
    params = {
        "auth_date": str(int(time.time()) - age_s),
        "query_id": "AAF_qa_query",
        "user": user,
    }
    dcs = "\n".join(f"{k}={params[k]}" for k in sorted(params))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    params["hash"] = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
    return urllib.parse.urlencode(params)


def hdr(init: str) -> dict:
    return {"Authorization": f"tma {init}", "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def auth_qa() -> dict:
    return hdr(forge(QA_UID))


@pytest.fixture(scope="session")
def auth_qa_b() -> dict:
    return hdr(forge(QA_UID_B))


def _mysql(sql: str) -> str:
    """Run one statement against the local DB and return raw tab-separated stdout."""
    cmd = [
        "mysql",
        f"-h{os.getenv('DB_HOST')}",
        f"-P{os.getenv('DB_PORT')}",
        f"-u{os.getenv('DB_LOGIN')}",
        f"-p{os.getenv('DB_PASSWORD')}",
        "--default-character-set=utf8mb4",  # Cyrillic mangles without this
        "-N",
        "-B",
        os.getenv("DB_NAME"),
        "-e",
        sql,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip())
    return out.stdout.strip()


@pytest.fixture
def db():
    return _mysql


def scalar(sql: str):
    v = _mysql(sql)
    return None if v == "" else v


def char_col(character_id: int, col: str):
    return scalar(f"SELECT {col} FROM characters WHERE id={character_id}")
