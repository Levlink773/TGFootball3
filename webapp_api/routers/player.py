from fastapi import APIRouter, Depends, HTTPException
from aiogram.utils.web_app import WebAppInitData

from services.character_service import CharacterService
from webapp_api.auth import auth_user

player_router = APIRouter()


@player_router.get("/player")
async def get_player(auth: WebAppInitData = Depends(auth_user)):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")
    club = character.club
    return {
        "user_id": auth.user.id,
        "name": character.name,
        "position": character.position,
        "gender": character.gender,
        "exp": character.exp,
        "level": character.level,
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
        "tier": character.tier_cipher,
        "club": {"id": club.id, "name": club.name_club, "league": club.league} if club else None,
    }
