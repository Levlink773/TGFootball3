"""F4: /api/trainer/pick-stat sets sess['stat_claimed'] AFTER an await, so a
concurrent burst all pass the claim check and each award stat points.

Driven in-process (building a real done-session over HTTP is heavy) by injecting a
session and counting update_character_characteristic calls.
"""
import asyncio

import pytest

from conftest import QA_UID


@pytest.mark.asyncio
async def test_pick_stat_awards_exactly_once(monkeypatch):
    from webapp_api.routers import trainer
    from services.character_service import CharacterService

    calls = {"n": 0}

    class _Char:
        id = 6

    async def fake_get(*a, **k):
        # This is the await that opens the TOCTOU window in trainer_pick_stat.
        # Yield the loop so concurrent coroutines interleave deterministically,
        # exactly as a real DB round-trip would.
        await asyncio.sleep(0)
        return _Char()

    async def fake_update(*a, **k):
        calls["n"] += 1
        return None

    monkeypatch.setattr(CharacterService, "get_character", fake_get)
    monkeypatch.setattr(CharacterService, "update_character_characteristic", fake_update)

    trainer._sessions[QA_UID] = {
        "done": True,
        "stat_claimed": False,
        "stat_points": 4,
        "step": 10,
        "score": 40,
    }

    class _User:
        id = QA_UID

    class _Auth:
        user = _User()

    req = trainer.PickStat(stat="speed")

    async def one():
        try:
            return await trainer.trainer_pick_stat(req, _Auth())
        except Exception as e:  # 409 after the fix
            return e

    await asyncio.gather(*[one() for _ in range(20)])

    assert calls["n"] == 1, (
        f"TOCTOU: reward awarded {calls['n']}x for one session (expected 1)"
    )
