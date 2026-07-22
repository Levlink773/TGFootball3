#!/usr/bin/env python3
"""E2E smoke test for webapp_api against localhost:3004.

Run ON the VPS from /root/footballgame:  venv/bin/python scripts/qa_e2e.py
Signs initData with TEST_BOT_TOKEN for the first real character in the DB.
Prints only endpoint -> status/result lines; never prints tokens.
Read-mostly: the only writes it makes are the idempotent tutorial-complete,
and (optional, --write) one 30-min training start for the QA character.
"""
import asyncio
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.parse
import urllib.request

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from database.base_acces import get_base  # noqa: E402

get_base()
from sqlalchemy import select  # noqa: E402
from database.models.character import Character  # noqa: E402
from database.session import get_session  # noqa: E402

BASE = "http://127.0.0.1:3004/api"


async def first_user_id():
    async for s in get_session():
        row = (await s.execute(
            select(Character.characters_user_id)
            .where(Character.characters_user_id.isnot(None))
            .limit(1)
        )).first()
        return row[0] if row else None


def forge_init_data(user_id: int) -> str:
    token = os.getenv("TEST_BOT_TOKEN") or os.getenv("BOT_TOKEN")
    user = json.dumps({"id": int(user_id), "first_name": "QA", "username": "qa"},
                      separators=(",", ":"))
    params = {"auth_date": str(int(time.time())), "query_id": "AAQA", "user": user}
    dcs = "\n".join(f"{k}={params[k]}" for k in sorted(params))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    params["hash"] = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
    return urllib.parse.urlencode(params)


def call(init, path, method="GET"):
    req = urllib.request.Request(
        BASE + path, method=method,
        headers={"Authorization": f"tma {init}", "Content-Type": "application/json"},
        data=b"{}" if method == "POST" else None,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read()[:160].decode(errors="ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:160].decode(errors="ignore")
    except Exception as e:  # noqa: BLE001
        return "ERR", str(e)[:160]


def main():
    user_id = asyncio.run(first_user_id())
    if not user_id:
        print("NO CHARACTERS IN DB")
        sys.exit(1)
    init = forge_init_data(user_id)
    checks = [
        ("GET", "/player"), ("GET", "/training"), ("GET", "/team"),
        ("GET", "/team/join-list"), ("GET", "/statistics"), ("GET", "/trainer/session"),
        ("GET", "/tutorial"), ("POST", "/tutorial/complete"),
        ("GET", "/matches"), ("GET", "/leagues"), ("GET", "/hall-of-fame"), ("GET", "/shop"),
        ("GET", "/settings"),
    ]
    failed = 0
    for method, path in checks:
        st, body = call(init, path, method)
        ok = st == 200
        failed += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} {method} {path} {st} {body[:100] if not ok else ''}")
    if "--write" in sys.argv:
        req = urllib.request.Request(
            BASE + "/training/start", method="POST",
            headers={"Authorization": f"tma {init}", "Content-Type": "application/json"},
            data=json.dumps({"stat": "speed", "minutes": 30}).encode(),
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                print("PASS POST /training/start", r.status, r.read()[:120].decode())
        except urllib.error.HTTPError as e:
            print("INFO POST /training/start", e.code, e.read()[:120].decode())
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
