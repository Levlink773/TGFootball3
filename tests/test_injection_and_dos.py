"""F7 (HTML injection via club rename/description) and F11 (club-schema DoS)."""
import httpx
import pytest

from conftest import API, QA_UID, char_col

# QA_UID 3312785 owns club id 6.
CLUB_ID = 6


def _club_name():
    from conftest import scalar
    return scalar(f"SELECT name_club FROM clubs WHERE id={CLUB_ID}")


def test_rename_rejects_html(auth_qa):
    """F7: the bot renders club names with parse_mode=HTML into league broadcasts.
    A name with < / > injects markup (phishing link) or breaks the whole broadcast.
    The API must reject angle brackets."""
    original = _club_name()
    payload = "<a href='https://evil'>ФК"  # 22 chars, passes the length gate
    try:
        r = httpx.post(f"{API}/api/team/rename", headers=auth_qa,
                       json={"name": payload}, timeout=10)
        if r.status_code == 200:
            stored = _club_name()
            assert "<" not in stored and ">" not in stored, (
                f"HTML INJECTION: stored club name contains markup: {stored!r}"
            )
        else:
            assert r.status_code == 400, f"unexpected {r.status_code}: {r.text}"
    finally:
        from conftest import _mysql
        safe = original.replace("'", "''")
        _mysql(f"UPDATE clubs SET name_club='{safe}' WHERE id={CLUB_ID}")


def test_description_rejects_html(auth_qa):
    from conftest import scalar, _mysql
    original = scalar(f"SELECT description FROM clubs WHERE id={CLUB_ID}") or ""
    payload = "<b>x</b>"
    try:
        r = httpx.post(f"{API}/api/team/description", headers=auth_qa,
                       json={"text": payload}, timeout=10)
        if r.status_code == 200:
            stored = scalar(f"SELECT description FROM clubs WHERE id={CLUB_ID}") or ""
            assert "<" not in stored and ">" not in stored, (
                f"HTML INJECTION in description: {stored!r}"
            )
        else:
            assert r.status_code == 400
    finally:
        safe = original.replace("'", "''")
        _mysql(f"UPDATE clubs SET description='{safe}' WHERE id={CLUB_ID}")


@pytest.mark.asyncio
async def test_bogus_club_schema_does_not_break_registration(monkeypatch):
    """F11: club.schema is a free String(255) written from bot callback data.
    A value that is not a real formation must not break match registration for
    every member of that club."""
    from services.club_shemas_service import SchemaSerivce
    from services.match_character_service import MatchCharacterService

    assert SchemaSerivce._VALID_SCHEMAS, "could not derive valid schema names"
    assert SchemaSerivce._DEFAULT_SCHEMA in SchemaSerivce._VALID_SCHEMAS

    async def no_players(*a, **k):
        return []

    monkeypatch.setattr(
        MatchCharacterService, "get_charaters_club_in_match", no_players
    )

    class _Club:
        id = CLUB_ID
        schema = "character_is_enough_room"  # a real attribute, but not a formation

    from config import PositionCharacter

    class _Char:
        position_enum = PositionCharacter.ATTACKER

    # Before the fix this raised TypeError (bound method subscripted) -> 500 for
    # every member of the club.
    ok = await SchemaSerivce.character_is_enough_room(
        club=_Club(), match_id="qa-match", my_character=_Char()
    )
    assert isinstance(ok, bool)
