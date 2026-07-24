"""F3: services that session.merge() a DETACHED character/club write the whole
loaded row back, reverting concurrent atomic updates (coin duplication / reward loss).

Contrast with equip_item / update_character_club_id, which call session.add() before
merge() and therefore only write genuinely-changed columns (verified: not affected).
"""
import pytest

from conftest import char_col, _mysql

CHAR_ID = 6
CLUB_ID = 6


@pytest.mark.asyncio
async def test_unequip_does_not_revert_concurrent_money_change():
    """Load character -> another request changes money -> unequip must not undo it."""
    from services.character_service import CharacterService
    from services.items_service import ItemService

    before = int(char_col(CHAR_ID, "money"))
    try:
        # 1. a request loads the character (detached, money snapshot = `before`)
        stale = await CharacterService.get_character(character_user_id=3312785)
        assert stale is not None

        # 2. meanwhile another request atomically credits +777 (e.g. a Monobank payout)
        await CharacterService.update_money_character(
            character_id=CHAR_ID, amount_money_adjustment=777
        )
        mid = int(char_col(CHAR_ID, "money"))
        assert mid == before + 777

        # 3. the first request now finishes an unrelated unequip using its stale object
        await ItemService.unequip_item(character_obj=stale, category_item="BOOTS")

        after = int(char_col(CHAR_ID, "money"))
        assert after == before + 777, (
            f"MERGE CLOBBER: unequip reverted money {mid} -> {after} "
            f"(stale snapshot {before} written back over a concurrent credit)"
        )
    finally:
        _mysql(f"UPDATE characters SET money={before}, boots_id=NULL WHERE id={CHAR_ID}")


@pytest.mark.asyncio
async def test_transfer_owner_does_not_revert_concurrent_club_change():
    from services.club_service import ClubService

    before_energy = int(char_col(CLUB_ID, "energy_applied") or 0) if False else int(
        _mysql(f"SELECT energy_applied FROM clubs WHERE id={CLUB_ID}") or 0
    )
    before_owner = _mysql(f"SELECT owner_id FROM clubs WHERE id={CLUB_ID}")
    try:
        club = await ClubService.get_club(club_id=CLUB_ID)
        assert club is not None

        # concurrent atomic change to a DIFFERENT column of the same row
        _mysql(f"UPDATE clubs SET energy_applied = energy_applied + 500 WHERE id={CLUB_ID}")
        mid = int(_mysql(f"SELECT energy_applied FROM clubs WHERE id={CLUB_ID}"))
        assert mid == before_energy + 500

        await ClubService.transfer_club_owner(club=club, new_owner_id=int(before_owner))

        after = int(_mysql(f"SELECT energy_applied FROM clubs WHERE id={CLUB_ID}"))
        assert after == before_energy + 500, (
            f"MERGE CLOBBER: transfer_club_owner reverted energy_applied {mid} -> {after}"
        )
    finally:
        _mysql(
            f"UPDATE clubs SET energy_applied={before_energy}, owner_id={before_owner} "
            f"WHERE id={CLUB_ID}"
        )
