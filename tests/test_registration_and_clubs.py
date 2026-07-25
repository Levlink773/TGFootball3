"""In-app registration + club creation, and the join-list regression.

Registration used to be a chat FSM in the bot; the Mini App's only response to a
user without a character was a button that closed the webview. These cover the
endpoints that replaced it, plus the query bug that made every freshly created
club invisible to everyone else.

Needs the local stack: MySQL from .env and the API on 127.0.0.1:3004.
"""
import time

import pytest
import httpx

from conftest import API, QA_UID, QA_UID_ABSENT, forge, hdr, scalar


def _cleanup(uid: int):
    """Drop everything the absent-user tests create, FK-safe (characters and
    clubs both point at users.user_id)."""
    cid = scalar(f"SELECT id FROM characters WHERE characters_user_id={uid}")
    if cid:
        scalar(f"DELETE FROM reminder_characters WHERE character_id={cid}")
        scalar(f"UPDATE characters SET club_id=NULL WHERE id={cid}")
    club_id = scalar(f"SELECT id FROM clubs WHERE owner_id={uid}")
    if club_id:
        scalar(f"DELETE FROM club_infrastructures WHERE club_id={club_id}")
        scalar(f"DELETE FROM clubs WHERE id={club_id}")
    scalar(f"DELETE FROM characters WHERE characters_user_id={uid}")
    scalar(f"DELETE FROM users WHERE user_id={uid}")


@pytest.fixture
def fresh_uid(db):
    """A user id with no users row, cleaned up either side of the test."""
    _cleanup(QA_UID_ABSENT)
    yield QA_UID_ABSENT
    _cleanup(QA_UID_ABSENT)


@pytest.fixture
def auth_fresh(fresh_uid):
    return hdr(forge(fresh_uid))


# ── POST /character ───────────────────────────────────────────────────────────

def test_creates_user_row_for_app_only_player(auth_fresh, fresh_uid):
    """Someone who opens the Mini App from the menu button has never messaged the
    bot, so the middleware that inserts their users row never ran — and both
    characters.characters_user_id and clubs.owner_id are FKs to it."""
    assert scalar(f"SELECT user_id FROM users WHERE user_id={fresh_uid}") is None

    r = httpx.post(
        f"{API}/api/character",
        json={"name": "Тест Гравець", "gender": "MAN", "position": "ATTACKER"},
        headers=auth_fresh,
        timeout=10,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["created"] is True
    assert body["player"]["name"] == "Тест Гравець"
    assert body["player"]["position"] == "Нападник"  # .value, matching GET /player

    assert scalar(f"SELECT user_id FROM users WHERE user_id={fresh_uid}") is not None
    cid = scalar(f"SELECT id FROM characters WHERE characters_user_id={fresh_uid}")
    assert cid is not None
    # Locked-keyboard limbo: every bot button stays 🔒 until END_TRAINING, and the
    # chat flow that used to clear it is gone.
    assert scalar(f"SELECT status_register FROM users WHERE user_id={fresh_uid}") == "END_TRAINING"
    # education handlers dereference character.reminder unguarded
    assert scalar(f"SELECT id FROM reminder_characters WHERE character_id={cid}") is not None
    # 150 energy and the position's starting stats, same as the bot FSM produced
    assert scalar(f"SELECT current_energy FROM characters WHERE id={cid}") == "150"


def test_second_create_is_idempotent_not_an_error(auth_fresh):
    """A double tap, a retry after the client's 20s abort, and "already registered
    in the old bot FSM" are the same case — none of them is an error state, and
    none of them may overwrite the existing character."""
    first = httpx.post(
        f"{API}/api/character",
        json={"name": "Перше Імя", "gender": "WOMAN", "position": "GOALKEEPER"},
        headers=auth_fresh,
        timeout=10,
    ).json()
    assert first["created"] is True

    r = httpx.post(
        f"{API}/api/character",
        json={"name": "Друге Імя", "gender": "MAN", "position": "ATTACKER"},
        headers=auth_fresh,
        timeout=10,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["created"] is False
    assert body["player"]["name"] == "Перше Імя"
    assert body["player"]["position"] == "Воротар"


def test_existing_character_is_never_mutated(auth_qa):
    """QA_UID already has a character; the endpoint must report it, not rewrite it."""
    before = httpx.get(f"{API}/api/player", headers=auth_qa, timeout=10).json()
    r = httpx.post(
        f"{API}/api/character",
        json={"name": "Підміна", "gender": "WOMAN", "position": "DEFENDER"},
        headers=auth_qa,
        timeout=10,
    )
    assert r.status_code == 200, r.text
    assert r.json()["created"] is False
    after = httpx.get(f"{API}/api/player", headers=auth_qa, timeout=10).json()
    assert after["name"] == before["name"]
    assert after["position"] == before["position"]


@pytest.mark.parametrize("name", [
    "x",                       # under the minimum
    "  ",                      # whitespace only
    "x" * 21,                  # over the maximum
    "<b>Іван</b>",             # HTML — names are interpolated into parse_mode=HTML broadcasts
    "Іван <script>",
    "Іван 🙂",                 # emoji
])
def test_rejects_bad_names(auth_fresh, name):
    r = httpx.post(
        f"{API}/api/character",
        json={"name": name, "gender": "MAN", "position": "ATTACKER"},
        headers=auth_fresh,
        timeout=10,
    )
    assert r.status_code == 400, f"{name!r} was accepted: {r.text}"


@pytest.mark.parametrize("payload", [
    {"name": "Норм Імя", "gender": "X", "position": "ATTACKER"},
    {"name": "Норм Імя", "gender": "MAN", "position": "STRIKER"},
    {"name": "Норм Імя", "gender": "Чоловік", "position": "ATTACKER"},  # .value, not member name
])
def test_rejects_unknown_gender_or_position(auth_fresh, payload):
    r = httpx.post(f"{API}/api/character", json=payload, headers=auth_fresh, timeout=10)
    assert r.status_code == 400, r.text


def test_options_expose_starting_stats(auth_qa):
    """The wizard reads its position stats from here rather than hardcoding them,
    so they cannot drift from const_character.py."""
    r = httpx.get(f"{API}/api/character/options", headers=auth_qa, timeout=10)
    assert r.status_code == 200, r.text
    body = r.json()
    assert {g["key"] for g in body["genders"]} == {"MAN", "WOMAN"}
    assert {p["key"] for p in body["positions"]} == {
        "GOALKEEPER", "DEFENDER", "MIDFIELDER", "ATTACKER"
    }
    for p in body["positions"]:
        assert set(p["stats"]) == {"technique", "kicks", "ball_selection", "speed", "endurance"}
        assert all(v > 0 for v in p["stats"].values())


# ── POST /team/create and the join-list regression ────────────────────────────

def test_create_club_wires_up_all_three_writes(auth_fresh, fresh_uid):
    """Club creation is three writes in three sessions. Skipping the third leaves a
    club whose GET /team returns infrastructure: null but still looks plausible."""
    httpx.post(
        f"{API}/api/character",
        json={"name": "Засновник", "gender": "MAN", "position": "MIDFIELDER"},
        headers=auth_fresh,
        timeout=10,
    )
    name = f"QA Клуб {int(time.time())}"
    r = httpx.post(f"{API}/api/team/create", json={"name": name}, headers=auth_fresh, timeout=10)
    assert r.status_code == 200, r.text
    club_id = r.json()["club_id"]

    assert scalar(f"SELECT owner_id FROM clubs WHERE id={club_id}") == str(fresh_uid)
    assert scalar(f"SELECT club_id FROM characters WHERE characters_user_id={fresh_uid}") == str(club_id)
    assert scalar(f"SELECT id FROM club_infrastructures WHERE club_id={club_id}") is not None

    team = httpx.get(f"{API}/api/team", headers=auth_fresh, timeout=10).json()
    assert team["club"]["is_owner"] is True
    assert team["club"]["members_count"] == 1
    assert team["infrastructure"] is not None


def test_empty_club_is_visible_to_other_players(auth_fresh, auth_qa):
    """THE regression. get_all_clubs_to_join counted members with an INNER join, so
    a club with zero members produced no row and vanished from the list — which on
    a freshly wiped database meant every club was invisible and nobody could ever
    join one. Emptied here rather than newly created, because a real create
    immediately puts its owner in it."""
    httpx.post(
        f"{API}/api/character",
        json={"name": "Порожняк", "gender": "MAN", "position": "DEFENDER"},
        headers=auth_fresh,
        timeout=10,
    )
    name = f"QA Порожній {int(time.time())}"
    club_id = httpx.post(
        f"{API}/api/team/create", json={"name": name}, headers=auth_fresh, timeout=10
    ).json()["club_id"]

    scalar(f"UPDATE characters SET club_id=NULL WHERE characters_user_id={QA_UID_ABSENT}")
    assert scalar(f"SELECT COUNT(*) FROM characters WHERE club_id={club_id}") == "0"

    listing = httpx.get(f"{API}/api/team/join-list", headers=auth_qa, timeout=10).json()
    entry = next((c for c in listing["clubs"] if c["id"] == club_id), None)
    assert entry is not None, "an empty club must still appear in the join list"
    # count(*) over an outer join would report the all-NULL row as 1 member
    assert entry["members_count"] == 0


def test_join_list_hides_invite_only_clubs(auth_fresh, auth_qa):
    """The app has no join-request flow, so an invite-only club could only render a
    dead "за запрошенням" row that POST /team/join would 409 anyway."""
    httpx.post(
        f"{API}/api/character",
        json={"name": "Закритий", "gender": "MAN", "position": "ATTACKER"},
        headers=auth_fresh,
        timeout=10,
    )
    name = f"QA Закритий {int(time.time())}"
    club_id = httpx.post(
        f"{API}/api/team/create", json={"name": name}, headers=auth_fresh, timeout=10
    ).json()["club_id"]
    scalar(f"UPDATE clubs SET is_invite_only=1 WHERE id={club_id}")

    listing = httpx.get(f"{API}/api/team/join-list", headers=auth_qa, timeout=10).json()
    assert all(c["id"] != club_id for c in listing["clubs"])


def test_cannot_create_a_second_club(auth_fresh):
    httpx.post(
        f"{API}/api/character",
        json={"name": "Дубль", "gender": "MAN", "position": "ATTACKER"},
        headers=auth_fresh,
        timeout=10,
    )
    first = f"QA Один {int(time.time())}"
    assert httpx.post(
        f"{API}/api/team/create", json={"name": first}, headers=auth_fresh, timeout=10
    ).status_code == 200
    r = httpx.post(
        f"{API}/api/team/create", json={"name": f"{first} два"}, headers=auth_fresh, timeout=10
    )
    assert r.status_code == 409, r.text


def test_duplicate_club_name_rejected(auth_fresh):
    httpx.post(
        f"{API}/api/character",
        json={"name": "Тезка", "gender": "MAN", "position": "ATTACKER"},
        headers=auth_fresh,
        timeout=10,
    )
    taken = scalar("SELECT name_club FROM clubs WHERE is_fake_club=0 LIMIT 1")
    if not taken:
        pytest.skip("no real club in the local DB to collide with")
    r = httpx.post(f"{API}/api/team/create", json={"name": taken}, headers=auth_fresh, timeout=10)
    assert r.status_code == 409, r.text


@pytest.mark.parametrize("name", ["ab", "x" * 31, "Клуб <b>"])
def test_rejects_bad_club_names(auth_fresh, name):
    httpx.post(
        f"{API}/api/character",
        json={"name": "Назвач", "gender": "MAN", "position": "ATTACKER"},
        headers=auth_fresh,
        timeout=10,
    )
    r = httpx.post(f"{API}/api/team/create", json={"name": name}, headers=auth_fresh, timeout=10)
    assert r.status_code == 400, r.text


def test_create_club_requires_a_character(auth_fresh):
    r = httpx.post(
        f"{API}/api/team/create", json={"name": "Без Гравця"}, headers=auth_fresh, timeout=10
    )
    assert r.status_code == 404, r.text


# ── tutorial decoupling ───────────────────────────────────────────────────────

def test_tutorial_still_pending_after_in_app_registration(auth_fresh):
    """Registration sets END_TRAINING, which GET /tutorial used to derive
    `completed` from — so without users.tutorial_completed_at the 5 slides would
    silently never run for anyone registering in the app."""
    httpx.post(
        f"{API}/api/character",
        json={"name": "Новачок", "gender": "MAN", "position": "ATTACKER"},
        headers=auth_fresh,
        timeout=10,
    )
    assert httpx.get(f"{API}/api/tutorial", headers=auth_fresh, timeout=10).json()["completed"] is False
    httpx.post(f"{API}/api/tutorial/complete", headers=auth_fresh, timeout=10)
    assert httpx.get(f"{API}/api/tutorial", headers=auth_fresh, timeout=10).json()["completed"] is True
