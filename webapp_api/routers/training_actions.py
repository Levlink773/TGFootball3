"""Write-endpoints for training + education center — bot-parity logic.

Gym completion normally runs as an asyncio task inside the bot process; the API
is a separate process, so app-started trainings are completed LAZILY here: any
GET /api/training (or explicit finish) applies an elapsed training's outcome.
Double-payout is prevented by an atomic conditional flip of
reminder_characters.character_in_training (True -> False) — whichever process
flips it first owns the payout (the bot's Gym._run_training re-checks the same
flag before paying).
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import update
from aiogram.utils.web_app import WebAppInitData

from constants import (
    CHANCE_VIP_PASS,
    DELTA_TIME_EDUCATION_REWARD,
    X2_REWARD_WEEKEND_START_DAY,
    X2_REWARD_WEEKEND_END_DAY,
    chance_add_point,
    const_energy_by_time,
    const_name_characteristics,
)
from bot.club_infrastructure.config import INFRASTRUCTURE_BONUSES
from bot.club_infrastructure.types import InfrastructureType
from bot.routers.gym.education_center import calculation_bonus
from database.models.reminder_character import ReminderCharacter
from database.session import get_session
from services.character_service import CharacterService
from services.club_infrastructure_service import ClubInfrastructureService
from services.reminder_character_service import RemniderCharacterService
from utils.randomaizer import check_chance

from webapp_api.auth import auth_user

training_actions_router = APIRouter()

ALLOWED_MINUTES = (30, 60, 90, 120)


class StartTraining(BaseModel):
    stat: str
    minutes: int


async def _flip_in_training(character_id: int, to: bool) -> bool:
    """Atomic conditional flip; returns True if this call won the flip."""
    async for session in get_session():
        async with session.begin():
            res = await session.execute(
                update(ReminderCharacter)
                .where(
                    ReminderCharacter.character_id == character_id,
                    ReminderCharacter.character_in_training == (not to),
                )
                .values(character_in_training=to)
            )
            return res.rowcount == 1
    return False


async def complete_elapsed_training(character) -> dict | None:
    """Apply outcome of an elapsed training (bot Gym._run_training parity)."""
    reminder = character.reminder
    if not (reminder and reminder.character_in_training and reminder.time_start_training):
        return None
    ends_at = reminder.time_start_training + timedelta(seconds=reminder.time_training_seconds or 0)
    if datetime.now() < ends_at:
        return None
    if not await _flip_in_training(character.id, to=False):
        return None  # bot (or a parallel request) owns this completion

    duration = timedelta(seconds=reminder.time_training_seconds or 0)
    chance = chance_add_point.get(duration, 35)
    if character.vip_pass_is_active:
        chance += CHANCE_VIP_PASS
    if character.club_id:
        infra = await ClubInfrastructureService.get_infrastructure(club_id=character.club_id)
        if infra:
            chance += INFRASTRUCTURE_BONUSES[InfrastructureType.TRAINING_BASE].get(
                level=infra.get_infrastructure_level(InfrastructureType.TRAINING_BASE)
            )

    success = check_chance(chance)
    points = 2 if X2_REWARD_WEEKEND_START_DAY <= datetime.now().day <= X2_REWARD_WEEKEND_END_DAY else 1
    stat = reminder.training_stats
    if success and stat in const_name_characteristics:
        await CharacterService.update_character_characteristic(
            character_id=character.id,
            type_characteristic=stat,
            amount_add_points=points,
        )
    await CharacterService.add_count_go_to_gym(character.id, 1)
    await RemniderCharacterService.anulate_training_character(character.id)
    return {"success": success, "stat": stat, "points": points if success else 0}


@training_actions_router.post("/training/start")
async def start_training(req: StartTraining, auth: WebAppInitData = Depends(auth_user)):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")
    if req.stat not in const_name_characteristics:
        raise HTTPException(status_code=400, detail="Невідома характеристика")
    if req.minutes not in ALLOWED_MINUTES:
        raise HTTPException(status_code=400, detail="Недопустима тривалість")

    duration = timedelta(minutes=req.minutes)
    cost = const_energy_by_time[duration]
    if character.current_energy < cost:
        raise HTTPException(status_code=409, detail=f"Не вистачає енергії: потрібно {cost}")

    # lazily settle a finished training first, then claim the slot atomically
    await complete_elapsed_training(character)
    if not character.reminder:
        await RemniderCharacterService.create_character_reminder(character.id)
    if not await _flip_in_training(character.id, to=True):
        raise HTTPException(status_code=409, detail="Персонаж вже тренується")

    # ponytail: SPORTS_MEDICINE time reduction not applied to app-started
    # trainings (bot applies it); upgrade path = store reduced seconds + original
    # duration key so chance lookup survives.
    await RemniderCharacterService.update_training_info(
        character_id=character.id,
        training_stats=req.stat,
        time_start_training=datetime.now(),
        time_training_seconds=duration.total_seconds(),
    )
    await CharacterService.consume_energy(character_id=character.id, energy_consumed=cost)

    return {
        "started": True,
        "stat": req.stat,
        "minutes": req.minutes,
        "energy_cost": cost,
        "chance": chance_add_point[duration] + (CHANCE_VIP_PASS if character.vip_pass_is_active else 0),
        "ends_at": (datetime.now() + duration).isoformat(),
    }


@training_actions_router.post("/education/claim")
async def claim_education(auth: WebAppInitData = Depends(auth_user)):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character or not character.reminder:
        raise HTTPException(status_code=404, detail="No character")

    now = datetime.now()
    # atomic idempotency gate: push the cooldown forward only if it has expired
    async for session in get_session():
        async with session.begin():
            res = await session.execute(
                update(ReminderCharacter)
                .where(
                    ReminderCharacter.character_id == character.id,
                    ReminderCharacter.education_reward_date <= now,
                )
                .values(education_reward_date=now + DELTA_TIME_EDUCATION_REWARD)
            )
            claimed = res.rowcount == 1
    if not claimed:
        left = int((character.reminder.education_reward_date - now).total_seconds())
        raise HTTPException(status_code=409, detail=f"Нагорода ще не готова ({max(0, left)} c)")

    exp, coins, energy = await calculation_bonus(character)
    await CharacterService.edit_character_energy(character_id=character.id, amount_energy=energy)
    await CharacterService.add_exp_character(character_id=character.id, amount_exp_add=exp)
    await CharacterService.update_money_character(character_id=character.id, amount_money_adjustment=coins)

    return {"claimed": True, "exp": exp, "coins": coins, "energy": energy}
