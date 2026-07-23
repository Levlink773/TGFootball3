from datetime import date

from sqlalchemy import select, update
from sqlalchemy.dialects.mysql import insert as mysql_insert

from database.models.daily_quest import DailyQuest
from database.session import get_session

# Daily targets and completion reward.
# ponytail: hardcoded values pending Maxim's sign-off; move to constants.py if tuned.
QUEST_TARGETS = {"trainings": 3, "matches": 2, "wins": 1}
QUEST_REWARD = {"coins": 50, "energy": 25}
GIFT_REWARD = {"coins_min": 10, "coins_max": 50, "energy": 10}


class DailyQuestService:

    @classmethod
    async def get_today(cls, character_id: int) -> DailyQuest:
        today = date.today()
        async for session in get_session():
            async with session.begin():
                # upsert keeps concurrent first-calls race-safe via the unique key
                await session.execute(
                    mysql_insert(DailyQuest)
                    .values(character_id=character_id, quest_date=today)
                    .prefix_with("IGNORE")
                )
                result = await session.execute(
                    select(DailyQuest).where(
                        DailyQuest.character_id == character_id,
                        DailyQuest.quest_date == today,
                    )
                )
                return result.scalar_one()

    @classmethod
    async def increment(cls, character_id: int, field: str) -> None:
        if field not in QUEST_TARGETS:
            return
        await cls.get_today(character_id)  # ensure row exists
        col = getattr(DailyQuest, field)
        async for session in get_session():
            async with session.begin():
                await session.execute(
                    update(DailyQuest)
                    .where(
                        DailyQuest.character_id == character_id,
                        DailyQuest.quest_date == date.today(),
                        col < QUEST_TARGETS[field],
                    )
                    .values({field: col + 1})
                )
                await session.commit()

    @classmethod
    async def claim_gift(cls, character_id: int) -> bool:
        # Atomic once-per-day gift flag, same pattern as claim()
        await cls.get_today(character_id)
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    update(DailyQuest)
                    .where(
                        DailyQuest.character_id == character_id,
                        DailyQuest.quest_date == date.today(),
                        DailyQuest.gift_claimed.is_(False),
                    )
                    .values(gift_claimed=True)
                )
                await session.commit()
                return result.rowcount > 0
        return False

    @classmethod
    async def claim(cls, character_id: int) -> bool:
        # Atomic claim: only flips claimed 0->1 when all targets are met.
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    update(DailyQuest)
                    .where(
                        DailyQuest.character_id == character_id,
                        DailyQuest.quest_date == date.today(),
                        DailyQuest.claimed.is_(False),
                        DailyQuest.trainings >= QUEST_TARGETS["trainings"],
                        DailyQuest.matches >= QUEST_TARGETS["matches"],
                        DailyQuest.wins >= QUEST_TARGETS["wins"],
                    )
                    .values(claimed=True)
                )
                await session.commit()
                return result.rowcount > 0
        return False
