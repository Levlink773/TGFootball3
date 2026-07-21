from collections import defaultdict

from fastapi import APIRouter, Depends
from aiogram.utils.web_app import WebAppInitData

from constants import PositionCharacter

from services.character_service import CharacterService
from services.match_character_service import MatchCharacterService

from utils.redis_cache import cached_json
from webapp_api.auth import auth_user

hall_of_fame_router = APIRouter()

TOP_N = 15


def _rank(entries: list[dict], user_id: int) -> dict:
    """entries sorted desc; returns top-N + requesting user's place."""
    my = next(
        ({"place": i + 1, **e} for i, e in enumerate(entries) if e["user_id"] == user_id),
        None,
    )
    return {"top": entries[:TOP_N], "me": my}


async def _build_ratings() -> dict:
    characters = await CharacterService.get_all_characters_not_bot()
    by_id = {c.id: c for c in characters}

    def char_entry(c, value):
        return {
            "user_id": c.characters_user_id,
            "name": c.character_name,
            "position": c.acronym_position,
            "value": value,
        }

    power = sorted(characters, key=lambda c: c.full_power, reverse=True)
    level = sorted(characters, key=lambda c: c.exp, reverse=True)

    positions = {}
    for pos in PositionCharacter:
        pos_chars = [c for c in characters if c.position_enum == pos]
        pos_chars.sort(key=lambda c: c.full_power, reverse=True)
        positions[pos.name] = {
            "label": pos.value,
            "entries": [char_entry(c, round(c.full_power, 2)) for c in pos_chars],
        }

    month_matches = await MatchCharacterService.get_match_characters_by_one_month() or []
    mvp_scores: dict[int, float] = defaultdict(float)
    goals: dict[int, int] = defaultdict(int)
    for m in month_matches:
        mvp_scores[m.character_id] += m.count_score
        goals[m.character_id] += m.goals_count

    def aggregate(source: dict) -> list[dict]:
        rows = []
        for character_id, value in sorted(source.items(), key=lambda kv: kv[1], reverse=True):
            c = by_id.get(character_id)
            if not c:
                continue
            rows.append(char_entry(c, round(value, 2)))
        return rows

    return {
        "power": [char_entry(c, round(c.full_power, 2)) for c in power],
        "level": [char_entry(c, c.level) for c in level],
        "mvp": aggregate(mvp_scores),
        "bombers": aggregate(goals),
        "positions": positions,
    }


@hall_of_fame_router.get("/hall-of-fame")
async def get_hall_of_fame(auth: WebAppInitData = Depends(auth_user)):
    data = await cached_json("webapp:hall_of_fame", ttl=60, producer=_build_ratings)
    user_id = auth.user.id
    return {
        "power": _rank(data["power"], user_id),
        "level": _rank(data["level"], user_id),
        "mvp": _rank(data["mvp"], user_id),
        "bombers": _rank(data["bombers"], user_id),
        "positions": {
            key: {"label": block["label"], **_rank(block["entries"], user_id)}
            for key, block in data["positions"].items()
        },
    }
