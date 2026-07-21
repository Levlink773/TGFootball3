import json
import logging
from typing import Any, Awaitable, Callable

from redis.asyncio import Redis

# db=1: db=0 belongs to the FootballBlitz app on the same VPS
redis = Redis(host="127.0.0.1", port=6379, db=1, decode_responses=True)

# ponytail: JSON-only cache helper for read-mostly data (ratings, league tables,
# Mini App API responses). Not for balances/energy — those need write-through
# invalidation; add invalidate(key) calls at write paths when that day comes.
async def cached_json(key: str, ttl: int, producer: Callable[[], Awaitable[Any]]) -> Any:
    try:
        hit = await redis.get(key)
        if hit is not None:
            return json.loads(hit)
    except Exception as e:
        logging.warning("redis get failed for %s: %s", key, e)
        return await producer()
    value = await producer()
    try:
        await redis.set(key, json.dumps(value, ensure_ascii=False), ex=ttl)
    except Exception as e:
        logging.warning("redis set failed for %s: %s", key, e)
    return value


async def invalidate(key: str) -> None:
    try:
        await redis.delete(key)
    except Exception as e:
        logging.warning("redis delete failed for %s: %s", key, e)
