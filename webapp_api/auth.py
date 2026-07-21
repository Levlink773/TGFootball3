"""Telegram Mini App auth.

Every request must carry `Authorization: tma <initData>`. The initData is
validated with aiogram's HMAC check against BOT_TOKEN on EVERY method —
no GET/OPTIONS bypass, no ?user_id= fallback (both were flaws in the
FootballBlitz webapp this deliberately does not inherit).
"""
from fastapi import Header, HTTPException
from aiogram.utils.web_app import safe_parse_webapp_init_data, WebAppInitData

from config import BOT_TOKEN

MAX_INITDATA_AGE_SECONDS = 60 * 60 * 24  # Telegram re-issues initData per launch


def auth_user(authorization: str = Header(default="")) -> WebAppInitData:
    scheme, _, init_data = authorization.partition(" ")
    if scheme.lower() != "tma" or not init_data:
        raise HTTPException(status_code=401, detail="Missing initData")
    try:
        parsed = safe_parse_webapp_init_data(token=BOT_TOKEN, init_data=init_data)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid initData")
    if parsed.user is None:
        raise HTTPException(status_code=401, detail="No user in initData")
    import time
    if parsed.auth_date and (time.time() - parsed.auth_date.timestamp()) > MAX_INITDATA_AGE_SECONDS:
        raise HTTPException(status_code=401, detail="initData expired")
    return parsed
