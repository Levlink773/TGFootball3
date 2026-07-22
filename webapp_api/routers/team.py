"""Команда (club) — read + join/leave, mirroring bot club menu logic.

Owner management (kick/transfer/schema/etc.) stays in the bot for now; the app
covers what regular players need daily. (ponytail: owner tools = next block.)
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from aiogram.utils.web_app import WebAppInitData

from config import LINK_TO_CHAT
from constants import MAX_LEN_MEMBERS_CLUB, TIME_TO_JOIN_TO_CLUB
from bot.club_infrastructure.config import INFRASTRUCTURE_BONUSES, UPGRADE_COSTS
from bot.club_infrastructure.types import InfrastructureType
from services.character_service import CharacterService
from services.club_service import ClubService
from services.club_infrastructure_service import ClubInfrastructureService

from webapp_api.auth import auth_user

team_router = APIRouter()

INFRA_LABELS = {
    InfrastructureType.TRAINING_BASE: "🏋‍♂ Тренувальна база",
    InfrastructureType.TRAINING_CENTER: "📚 Навчальний центр",
    InfrastructureType.PREMIUM_FOND: "🏆 Преміальний фонд",
    InfrastructureType.STADIUM: "🏟 Стадіон",
    InfrastructureType.SPORTS_MEDICINE: "🏥 Спортивна медицина",
    InfrastructureType.ACADEMY_TALENT: "🌟 Академія талантів",
}


def _member_entry(ch, me_user_id):
    return {
        "user_id": ch.characters_user_id,
        "name": ch.name,
        "full_power": round(ch.full_power, 2),
        "level": ch.level,
        "position": ch.position,
        "is_me": ch.characters_user_id == me_user_id,
    }


@team_router.get("/team")
async def get_team(auth: WebAppInitData = Depends(auth_user)):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")

    if not character.club_id:
        return {"club": None, "chat_url": LINK_TO_CHAT}

    club = await ClubService.get_club(club_id=character.club_id)
    if not club:
        return {"club": None, "chat_url": LINK_TO_CHAT}

    members = sorted(club.characters, key=lambda c: c.full_power, reverse=True)
    infra = await ClubInfrastructureService.get_infrastructure(club_id=club.id)
    infrastructure = None
    if infra:
        objects = []
        for itype in InfrastructureType:
            level = infra.get_infrastructure_level(itype)
            level_i = int(level.value)
            bonuses = INFRASTRUCTURE_BONUSES[itype]
            objects.append({
                "type": itype.name,
                "label": INFRA_LABELS[itype],
                "level": level_i,
                "bonus": bonuses.get(level=level),
                "next_cost": UPGRADE_COSTS.get(level.get_next_level()) if level_i < 5 else None,
            })
        infrastructure = {"points": infra.points, "objects": objects}

    return {
        "club": {
            "id": club.id,
            "name": club.name_club,
            "league": club.league,
            "description": club.description,
            "total_power": round(club.total_power, 2),
            "members_count": len(club.characters),
            "max_members": MAX_LEN_MEMBERS_CLUB,
            "is_owner": club.owner_id == auth.user.id,
            "invite_only": bool(club.is_invite_only),
            "stadium_name": club.custom_name_stadion,
            "chat_url": club.link_to_chat,
            "members": [_member_entry(c, auth.user.id) for c in members],
        },
        "chat_url": LINK_TO_CHAT,
        "infrastructure": infrastructure,
    }


@team_router.get("/team/join-list")
async def join_list(auth: WebAppInitData = Depends(auth_user)):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")
    clubs = await ClubService.get_all_clubs_to_join()
    return {
        "clubs": [
            {
                "id": c.id,
                "name": c.name_club,
                "league": c.league,
                "members_count": len(c.characters),
                "max_members": MAX_LEN_MEMBERS_CLUB,
                "total_power": round(c.total_power, 2),
                "invite_only": bool(c.is_invite_only),
            }
            for c in clubs
        ]
    }


class JoinClub(BaseModel):
    club_id: int


@team_router.post("/team/join")
async def join_club(req: JoinClub, auth: WebAppInitData = Depends(auth_user)):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")
    if character.club_id:
        raise HTTPException(status_code=409, detail="Ти вже в команді — спочатку покинь її")

    club = await ClubService.get_club(club_id=req.club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Команду не знайдено")
    if club.is_invite_only:
        raise HTTPException(status_code=409, detail="Ця команда приймає лише за запрошенням — подай заявку в боті")
    if len(club.characters) >= MAX_LEN_MEMBERS_CLUB:
        raise HTTPException(status_code=409, detail="Команда заповнена (11/11)")
    if character.reminder and character.reminder.time_to_join_club:
        ready_at = character.reminder.time_to_join_club + TIME_TO_JOIN_TO_CLUB
        if datetime.now() < ready_at:
            left = int((ready_at - datetime.now()).total_seconds())
            raise HTTPException(status_code=409, detail=f"Зачекай {left} c перед вступом")

    await CharacterService.update_character_club_id(character=character, club_id=club.id)
    return {"joined": True, "club_id": club.id, "club_name": club.name_club}


@team_router.post("/team/leave")
async def leave_club(auth: WebAppInitData = Depends(auth_user)):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")
    if not character.club_id:
        raise HTTPException(status_code=409, detail="Ти не в команді")
    club = await ClubService.get_club(club_id=character.club_id)
    if club and club.owner_id == auth.user.id:
        raise HTTPException(status_code=409, detail="Лідер не може покинути команду — передай лідерство в боті")
    await CharacterService.leave_club(character)
    return {"left": True}
