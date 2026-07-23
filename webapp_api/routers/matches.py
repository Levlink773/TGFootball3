from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from aiogram.utils.web_app import WebAppInitData

from constants_leagues import TypeLeague, GetConfig, NAMES_LEAGUES

from database.session import get_session
from database.models.blitz import Blitz
from database.models.blitz_character import BlitzCharacter

from blitz.exception import BlitzCloseError, CharacterExistsInBlitzError, MaxUsersInBlitzError
from blitz.services.blitz_service import BlitzService

from services.character_service import CharacterService
from services.daily_quest_service import DailyQuestService
from services.match_character_service import MatchCharacterService
from services.club_shemas_service import SchemaSerivce
from services.league_services.league_service import LeagueService

from webapp_api.routers.leagues import LEAGUE_SERVICES
from webapp_api.auth import auth_user

matches_router = APIRouter()

# Mirrors load_utils.py StartBlitzs schedule; stages N => 2^N teams, 2 players each
BLITZ_SCHEDULE = [
    {"time": "15:00", "stages_of_final": 4, "max_players": 2 ** 4 * 2},
    {"time": "19:00", "stages_of_final": 5, "max_players": 2 ** 5 * 2},
]


def _max_players_for(start_at: datetime) -> int:
    for slot in BLITZ_SCHEDULE:
        if start_at.strftime("%H:%M") == slot["time"]:
            return slot["max_players"]
    return BLITZ_SCHEDULE[0]["max_players"]


async def _get_character_or_404(user_id: int):
    character = await CharacterService.get_character(character_user_id=user_id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")
    return character


async def _next_blitz_state(character_id: int) -> dict | None:
    async for session in get_session():
        async with session.begin():
            result = await session.execute(
                select(Blitz)
                .where(Blitz.start_at > datetime.now())
                .order_by(Blitz.start_at.asc())
                .limit(1)
            )
            blitz = result.scalar_one_or_none()
            if not blitz:
                return None
            count = await session.scalar(
                select(func.count(BlitzCharacter.id)).where(BlitzCharacter.blitz_id == blitz.id)
            )
            mine = await session.scalar(
                select(func.count(BlitzCharacter.id))
                .where(BlitzCharacter.blitz_id == blitz.id)
                .where(BlitzCharacter.character_id == character_id)
            )
            return {
                "blitz_id": blitz.id,
                "start_at": blitz.start_at.isoformat(),
                "can_register": blitz.can_register,
                "registered": bool(mine),
                "participants": count,
                "max_players": _max_players_for(blitz.start_at),
            }


@matches_router.get("/matches")
async def get_matches(auth: WebAppInitData = Depends(auth_user)):
    character = await _get_character_or_404(auth.user.id)
    club = character.club

    leagues = []
    for type_league, service in LEAGUE_SERVICES.items():
        config = GetConfig.get_config(type_league)
        entry = {
            "type": type_league.value,
            "name": NAMES_LEAGUES[type_league],
            "is_active": config.league_is_active,
            "day_start": config.DAY_START,
            "day_end": config.DAY_END,
            "match_hour": config.HOUR_TIME_START_MATCH,
            "next_match": None,
        }
        if club:
            fight = await service.get_next_league_fight_by_club(club_id=club.id)
            if fight:
                registered = await MatchCharacterService.get_character_in_match(
                    match_id=fight.match_id,
                    group_id=fight.group_id,
                    club_id=club.id,
                    character_id=character.id,
                )
                opponent_id = (
                    fight.second_club_id if fight.first_club_id == club.id else fight.first_club_id
                )
                opponent = fight.second_club if fight.first_club_id == club.id else fight.first_club
                entry["next_match"] = {
                    "match_id": fight.match_id,
                    "time_to_start": fight.time_to_start.isoformat(),
                    "opponent_club_id": opponent_id,
                    "opponent_club_name": opponent.name_club if opponent else None,
                    "registered": bool(registered),
                }
        leagues.append(entry)

    return {
        "club": {"id": club.id, "name": club.name_club, "league": club.league} if club else None,
        "leagues": leagues,
        "blitz": {
            "schedule": BLITZ_SCHEDULE,
            "next": await _next_blitz_state(character.id),
        },
    }


class MatchRegisterBody(BaseModel):
    match_id: str


@matches_router.post("/match/register")
async def register_to_match(body: MatchRegisterBody, auth: WebAppInitData = Depends(auth_user)):
    character = await _get_character_or_404(auth.user.id)
    if character.reminder and character.reminder.character_in_training:
        raise HTTPException(status_code=409, detail="Персонаж на тренуванні")
    if not character.club_id:
        raise HTTPException(status_code=409, detail="У персонажа немає команди")

    fight = await LeagueService.get_league_fight(body.match_id)
    if not fight:
        raise HTTPException(status_code=404, detail="Матч не знайдено")
    if character.club_id not in (fight.first_club_id, fight.second_club_id):
        raise HTTPException(status_code=403, detail="Ваша команда не грає в цьому матчі")
    if datetime.now() > fight.time_to_start:
        raise HTTPException(status_code=409, detail="Матч уже почався")

    already = await MatchCharacterService.get_character_in_match(
        match_id=fight.match_id,
        group_id=fight.group_id,
        club_id=character.club_id,
        character_id=character.id,
    )
    if already:
        raise HTTPException(status_code=409, detail="Вже зареєстрований на матч")

    has_room = await SchemaSerivce.character_is_enough_room(
        club=character.club, match_id=fight.match_id, my_character=character
    )
    if not has_room:
        raise HTTPException(status_code=409, detail="Немає місця за схемою")

    ok = await MatchCharacterService.add_character_in_match(
        match_id=fight.match_id,
        club_id=character.club_id,
        group_id=fight.group_id,
        character_id=character.id,
    )
    if not ok:
        raise HTTPException(status_code=500, detail="Не вдалося зареєструватися")
    await CharacterService.add_count_register_on_match(character.id, 1)
    await DailyQuestService.increment(character.id, "matches")
    return {"ok": True, "match_id": fight.match_id}


@matches_router.post("/blitz/register")
async def register_to_blitz(auth: WebAppInitData = Depends(auth_user)):
    character = await _get_character_or_404(auth.user.id)
    state = await _next_blitz_state(character.id)
    if not state:
        raise HTTPException(status_code=409, detail="Немає запланованого бліцу")
    try:
        await BlitzService.add_character_to_blitz(
            state["blitz_id"], character, state["max_players"]
        )
    except BlitzCloseError:
        raise HTTPException(status_code=409, detail="Реєстрацію на бліц закрито")
    except CharacterExistsInBlitzError:
        raise HTTPException(status_code=409, detail="Вже зареєстрований на бліц")
    except MaxUsersInBlitzError:
        raise HTTPException(status_code=409, detail="Бліц заповнено")
    await DailyQuestService.increment(character.id, "matches")
    return {"ok": True, "blitz_id": state["blitz_id"]}
