from fastapi import APIRouter, Depends, HTTPException
from aiogram.utils.web_app import WebAppInitData

from database.models.character import Character
from services.character_service import CharacterService
from webapp_api.auth import auth_user

player_router = APIRouter()


def _xp_bounds(level: int) -> tuple[int, int | None]:
    """Floor + next-level exp for the XP progress bar (None next = max level)."""
    thresholds = Character.LEVEL_THRESHOLDS
    floor = thresholds[level - 2] if level >= 2 else 0
    nxt = thresholds[level - 1] if (level - 1) < len(thresholds) else None
    return floor, nxt


@player_router.get("/player")
async def get_player(auth: WebAppInitData = Depends(auth_user)):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")
    club = character.club
    exp_floor, exp_next = _xp_bounds(character.level)
    return {
        "user_id": auth.user.id,
        "name": character.name,
        "position": character.position,
        "gender": character.gender,
        "exp": character.exp,
        "level": character.level,
        "exp_floor": exp_floor,
        "exp_next": exp_next,
        "money": character.money,
        "energy": character.current_energy,
        "stats": {
            "technique": character.technique,
            "kicks": character.kicks,
            "ball_selection": character.ball_selection,
            "speed": character.speed,
            "endurance": character.endurance,
        },
        "full_power": character.full_power,
        "vip_active": character.vip_pass_is_active,
        "vip_until": character.vip_pass_expiration_date.isoformat() if character.vip_pass_expiration_date else None,
        "tier": character.tier_cipher,
        "club": {"id": club.id, "name": club.name_club, "league": club.league} if club else None,
    }
