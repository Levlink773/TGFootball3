"""Команда (club) — read + join/leave + owner moderation + infrastructure upgrade.

Owner tools (kick/transfer/rename/invite-only/description/upgrade) are exposed
here for the webapp; join-request approval stays in the bot (no requests table).
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from aiogram.utils.web_app import WebAppInitData

from config import LINK_TO_CHAT
from constants import MAX_LEN_MEMBERS_CLUB, TIME_TO_JOIN_TO_CLUB
from bot.club_infrastructure.config import INFRASTRUCTURE_BONUSES, UPGRADE_COSTS
from bot.club_infrastructure.types import InfrastructureType, InfrastructureLevel, InfrastructureTyping
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


def _infra_payload(infra):
    """Infra block: current levels + a per-level cost/bonus table for the UI."""
    objects = []
    for itype in InfrastructureType:
        level = infra.get_infrastructure_level(itype)
        level_i = int(level.value)
        bonuses = INFRASTRUCTURE_BONUSES[itype]
        levels = [
            {
                "level": int(lvl.value),
                "bonus": bonuses.get(level=lvl),
                "cost": UPGRADE_COSTS.get(lvl, 0) if int(lvl.value) >= 1 else 0,
            }
            for lvl in InfrastructureLevel
        ]
        objects.append({
            "type": itype.name,
            "label": INFRA_LABELS[itype],
            "level": level_i,
            "bonus": bonuses.get(level=level),
            "next_cost": UPGRADE_COSTS.get(level.get_next_level()) if level_i < 5 else None,
            "levels": levels,
        })
    return {"points": infra.points, "objects": objects}


def _member_entry(ch, me_user_id):
    return {
        "user_id": ch.characters_user_id,
        "name": ch.name,
        "full_power": round(ch.full_power, 2),
        "level": ch.level,
        "position": ch.position,
        "gender": ch.gender,
        "is_me": ch.characters_user_id == me_user_id,
    }


async def _owner_club(auth: WebAppInitData):
    """Resolve the caller's club and require them to be its owner."""
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character or not character.club_id:
        raise HTTPException(status_code=404, detail="Ти не в команді")
    club = await ClubService.get_club(club_id=character.club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Команду не знайдено")
    if club.owner_id != auth.user.id:
        raise HTTPException(status_code=403, detail="Тільки лідер команди")
    return club


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
    infrastructure = _infra_payload(infra) if infra else None

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


# ── Owner moderation (all owner-guarded via _owner_club) ──────────────────────

class UserIdReq(BaseModel):
    user_id: int


class RenameReq(BaseModel):
    name: str


class InviteOnlyReq(BaseModel):
    enabled: bool


class DescriptionReq(BaseModel):
    text: str


class UpgradeReq(BaseModel):
    type: str  # InfrastructureType member name, e.g. "TRAINING_CENTER"


@team_router.post("/team/kick")
async def kick_member(req: UserIdReq, auth: WebAppInitData = Depends(auth_user)):
    club = await _owner_club(auth)
    if req.user_id == auth.user.id:
        raise HTTPException(status_code=409, detail="Не можна вигнати себе")
    target = await CharacterService.get_character(character_user_id=req.user_id)
    if not target or target.club_id != club.id:
        raise HTTPException(status_code=404, detail="Гравця немає в команді")
    await ClubService.remove_character_from_club(target.id)
    return {"ok": True}


@team_router.post("/team/transfer")
async def transfer_owner(req: UserIdReq, auth: WebAppInitData = Depends(auth_user)):
    club = await _owner_club(auth)
    if req.user_id == auth.user.id:
        raise HTTPException(status_code=409, detail="Ти вже лідер")
    target = await CharacterService.get_character(character_user_id=req.user_id)
    if not target or target.club_id != club.id:
        raise HTTPException(status_code=404, detail="Гравця немає в команді")
    await ClubService.transfer_club_owner(club, req.user_id)
    return {"ok": True}


@team_router.post("/team/rename")
async def rename_team(req: RenameReq, auth: WebAppInitData = Depends(auth_user)):
    club = await _owner_club(auth)
    name = (req.name or "").strip()
    if not (3 <= len(name) <= 30):
        raise HTTPException(status_code=400, detail="Назва: від 3 до 30 символів")
    if not await ClubService.rename_club(club.id, name):
        raise HTTPException(status_code=409, detail="Така назва вже зайнята")
    return {"ok": True, "name": name}


@team_router.post("/team/invite-only")
async def set_invite_only(req: InviteOnlyReq, auth: WebAppInitData = Depends(auth_user)):
    club = await _owner_club(auth)
    await ClubService.change_status_invoice_invite(club.id, req.enabled)
    return {"ok": True, "invite_only": req.enabled}


@team_router.post("/team/description")
async def set_description(req: DescriptionReq, auth: WebAppInitData = Depends(auth_user)):
    club = await _owner_club(auth)
    text = (req.text or "").strip()
    if len(text) > 255:
        raise HTTPException(status_code=400, detail="Опис: до 255 символів")
    await ClubService.update_description_club(club.id, text or "Не вказано")
    return {"ok": True, "description": text}


@team_router.post("/team/infrastructure/upgrade")
async def upgrade_infrastructure(req: UpgradeReq, auth: WebAppInitData = Depends(auth_user)):
    club = await _owner_club(auth)
    try:
        itype = InfrastructureType[req.type]
    except KeyError:
        raise HTTPException(status_code=400, detail="Невідомий об'єкт")
    infra = await ClubInfrastructureService.get_infrastructure(club_id=club.id)
    if not infra:
        raise HTTPException(status_code=404, detail="Немає інфраструктури")
    level = infra.get_infrastructure_level(itype)
    if level == InfrastructureLevel.LEVEL_5:
        raise HTTPException(status_code=409, detail="Максимальний рівень")
    next_level = level.get_next_level()
    cost = UPGRADE_COSTS[next_level]
    # single atomic level-CAS + debit: concurrent clicks can't overcharge or skip a level
    ok = await ClubInfrastructureService.upgrade_if_current(
        club_id=club.id,
        column_name=InfrastructureTyping.get_name(itype),
        current_level=level,
        next_level=next_level,
        cost=cost,
    )
    if not ok:
        raise HTTPException(status_code=409, detail="Недостатньо очок або рівень уже змінено")
    infra = await ClubInfrastructureService.get_infrastructure(club_id=club.id)
    return {"ok": True, "infrastructure": _infra_payload(infra)}
