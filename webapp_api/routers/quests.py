import random

from fastapi import APIRouter, Depends, HTTPException
from aiogram.utils.web_app import WebAppInitData

from services.character_service import CharacterService
from pydantic import BaseModel

from services.daily_quest_service import (
    DailyQuestService, QUEST_TARGETS, QUEST_REWARDS, GIFT_REWARD, COMPLETION_BONUS_COINS,
)

from webapp_api.auth import auth_user

quests_router = APIRouter()


async def _get_character(auth: WebAppInitData):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")
    return character


_TITLES = {"trainings": "Проведи тренування", "matches": "Зіграй 2 матчі", "wins": "Здобудь перемогу"}


def _payload(q):
    quests = []
    for key, target in QUEST_TARGETS.items():
        current = getattr(q, key)
        claimed = getattr(q, f"{key}_claimed")
        quests.append({
            "key": key,
            "title": _TITLES[key],
            "current": current,
            "target": target,
            "reward_energy": QUEST_REWARDS[key],
            "claimable": current >= target and not claimed,
            "claimed": claimed,
        })
    all_claimed = all(x["claimed"] for x in quests)
    return {
        "quests": quests,
        "gift_claimed": q.gift_claimed,
        "bonus_coins": COMPLETION_BONUS_COINS,
        "bonus_claimable": all_claimed and not q.claimed,
        "bonus_claimed": q.claimed,
    }


@quests_router.get("/quests")
async def get_quests(auth: WebAppInitData = Depends(auth_user)):
    character = await _get_character(auth)
    q = await DailyQuestService.get_today(character.id)
    return _payload(q)


@quests_router.post("/gift/claim")
async def claim_gift(auth: WebAppInitData = Depends(auth_user)):
    character = await _get_character(auth)
    won = await DailyQuestService.claim_gift(character.id)
    if not won:
        raise HTTPException(status_code=409, detail="Подарунок уже отримано, приходь завтра")
    coins = random.randint(GIFT_REWARD["coins_min"], GIFT_REWARD["coins_max"])
    await CharacterService.update_money_character(
        character_id=character.id, amount_money_adjustment=coins
    )
    await CharacterService.edit_character_energy(
        character_id=character.id, amount_energy=GIFT_REWARD["energy"]
    )
    return {"ok": True, "coins": coins, "energy": GIFT_REWARD["energy"]}


@quests_router.post("/quests/claim-bonus")
async def claim_completion_bonus(auth: WebAppInitData = Depends(auth_user)):
    character = await _get_character(auth)
    won = await DailyQuestService.claim_completion_bonus(character.id)
    if not won:
        raise HTTPException(status_code=409, detail="Бонус недоступний")
    await CharacterService.update_money_character(
        character_id=character.id, amount_money_adjustment=COMPLETION_BONUS_COINS
    )
    q = await DailyQuestService.get_today(character.id)
    return _payload(q)


class ClaimRequest(BaseModel):
    key: str


@quests_router.post("/quests/claim")
async def claim_quest(req: ClaimRequest, auth: WebAppInitData = Depends(auth_user)):
    if req.key not in QUEST_TARGETS:
        raise HTTPException(status_code=400, detail="Невідоме завдання")
    character = await _get_character(auth)
    won = await DailyQuestService.claim_task(character.id, req.key)
    if not won:
        raise HTTPException(status_code=409, detail="Нагорода недоступна")
    energy = QUEST_REWARDS[req.key]
    await CharacterService.edit_character_energy(
        character_id=character.id, amount_energy=energy
    )
    q = await DailyQuestService.get_today(character.id)
    payload = _payload(q)
    payload["awarded_energy"] = energy
    return payload
