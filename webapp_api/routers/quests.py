import random

from fastapi import APIRouter, Depends, HTTPException
from aiogram.utils.web_app import WebAppInitData

from services.character_service import CharacterService
from services.daily_quest_service import DailyQuestService, QUEST_TARGETS, QUEST_REWARD, GIFT_REWARD

from webapp_api.auth import auth_user

quests_router = APIRouter()


async def _get_character(auth: WebAppInitData):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")
    return character


def _payload(q):
    done = all(getattr(q, f) >= t for f, t in QUEST_TARGETS.items())
    return {
        "quests": [
            {"key": "trainings", "title": "Проведи тренування", "current": q.trainings, "target": QUEST_TARGETS["trainings"]},
            {"key": "matches", "title": "Зіграй матч", "current": q.matches, "target": QUEST_TARGETS["matches"]},
            {"key": "wins", "title": "Переможи", "current": q.wins, "target": QUEST_TARGETS["wins"]},
        ],
        "reward": QUEST_REWARD,
        "claimable": done and not q.claimed,
        "claimed": q.claimed,
        "gift_claimed": q.gift_claimed,
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


@quests_router.post("/quests/claim")
async def claim_quests(auth: WebAppInitData = Depends(auth_user)):
    character = await _get_character(auth)
    won = await DailyQuestService.claim(character.id)
    if not won:
        raise HTTPException(status_code=409, detail="Нагорода недоступна")
    await CharacterService.update_money_character(
        character_id=character.id, amount_money_adjustment=QUEST_REWARD["coins"]
    )
    await CharacterService.edit_character_energy(
        character_id=character.id, amount_energy=QUEST_REWARD["energy"]
    )
    q = await DailyQuestService.get_today(character.id)
    return _payload(q)
