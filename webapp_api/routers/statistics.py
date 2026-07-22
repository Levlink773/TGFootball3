"""Статистика — personal career numbers + this-month match aggregates."""
from fastapi import APIRouter, Depends, HTTPException
from aiogram.utils.web_app import WebAppInitData

from services.character_service import CharacterService
from services.match_character_service import MatchCharacterService

from webapp_api.auth import auth_user

statistics_router = APIRouter()


@statistics_router.get("/statistics")
async def get_statistics(auth: WebAppInitData = Depends(auth_user)):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")

    month_rows = await MatchCharacterService.get_match_characters_by_one_month()
    mine = [r for r in month_rows if r.character_id == character.id]

    return {
        "career": {
            "trainings": character.count_go_to_gym or 0,
            "match_registrations": character.count_register_on_match or 0,
            "goals": character.count_goal_on_match or 0,
            "blitz_played": character.count_play_blitz or 0,
            "blitz_semifinals": character.count_rich_semi_final_blitz or 0,
            "blitz_finals": (character.count_rich_final_looser_blitz or 0)
            + (character.count_rich_final_winner_blitz or 0),
            "blitz_wins": character.count_rich_final_winner_blitz or 0,
            "mvp_2_plus": character.count_mvp_two_and_more or 0,
            "mvp_25_plus": character.count_mvp_two_half_and_more or 0,
            "mvp_3_plus": character.count_mvp_three_and_more or 0,
        },
        "month": {
            "matches": len(mine),
            "goals": sum(r.goals_count or 0 for r in mine),
            "mvp_score": round(sum(r.count_score or 0 for r in mine), 2),
        },
        "progress": {
            "level": character.level,
            "exp": character.exp,
            "full_power": round(character.full_power, 2),
            "money": character.money,
        },
    }
