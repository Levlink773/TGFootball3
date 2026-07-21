"""Forge valid Telegram WebApp initData for LOCAL testing.

Usage: .venv/bin/python scripts/forge_initdata.py [user_id]
Prints raw initData and a urlencoded ?initData= query value.
"""
import hashlib
import hmac
import json
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import BOT_TOKEN  # noqa: E402


def forge(user_id: int) -> str:
    user = json.dumps(
        {"id": user_id, "first_name": "Dev", "username": "dev_local", "language_code": "uk"},
        separators=(",", ":"),
    )
    pairs = {
        "auth_date": str(int(time.time())),
        "query_id": "AAF_dev_query",
        "user": user,
    }
    check_string = "\n".join(f"{k}={pairs[k]}" for k in sorted(pairs))
    secret = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    pairs["hash"] = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    return urllib.parse.urlencode(pairs)


if __name__ == "__main__":
    uid = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if uid is None:
        raise SystemExit("usage: forge_initdata.py <user_id>")
    raw = forge(uid)
    print(raw)
    print("---")
    print("?initData=" + urllib.parse.quote(raw, safe=""))
