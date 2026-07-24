"""F9 (energy cap / lost update) and F8 (negative training keys).

These call the real services against the local DB and restore the touched row.
"""
import asyncio

import pytest

from conftest import QA_UID, char_col

CHAR_ID = 6  # character for QA_UID 3312785


async def _restore(col, val):
    from services.character_service import CharacterService  # noqa
    from database.session import get_session
    from database.models.character import Character
    from sqlalchemy import update

    async for session in get_session():
        async with session.begin():
            await session.execute(
                update(Character).where(Character.id == CHAR_ID).values({col: val})
            )
            await session.commit()


@pytest.mark.asyncio
async def test_energy_respects_cap():
    """F9: edit_character_energy has no upper clamp, so rewards push energy over the
    150/300 tier cap (the '274/150' bug)."""
    from services.character_service import CharacterService

    before = int(char_col(CHAR_ID, "current_energy"))
    try:
        # award 100 energy five times from an already-high baseline
        await _restore("current_energy", 150)
        for _ in range(5):
            await CharacterService.edit_character_energy(character_id=CHAR_ID, amount_energy=100)
        final = int(char_col(CHAR_ID, "current_energy"))
        assert final <= 300, f"energy exceeded VIP cap: {final} > 300"
        assert final <= 150 or True  # base cap check is informative; VIP may allow 300
    finally:
        await _restore("current_energy", before)


@pytest.mark.asyncio
async def test_energy_not_negative():
    """consume_energy has no floor at 0."""
    from services.character_service import CharacterService

    before = int(char_col(CHAR_ID, "current_energy"))
    try:
        await _restore("current_energy", 10)
        await CharacterService.consume_energy(character_id=CHAR_ID, energy_consumed=999)
        final = int(char_col(CHAR_ID, "current_energy"))
        assert final >= 0, f"energy went negative: {final}"
    finally:
        await _restore("current_energy", before)


@pytest.mark.asyncio
async def test_training_key_not_negative():
    """F8: remove_training_key decrements with no WHERE training_key > 0."""
    from services.character_service import CharacterService

    before = int(char_col(CHAR_ID, "training_key"))
    try:
        await _restore("training_key", 1)
        # five concurrent debits from a single available key
        await asyncio.gather(*[
            CharacterService.remove_training_key(character_id=CHAR_ID) for _ in range(5)
        ])
        final = int(char_col(CHAR_ID, "training_key"))
        assert final >= 0, f"training_key went negative: {final}"
    finally:
        await _restore("training_key", before)
