"""Напоминание про щоденний подарунок (Max 26.07).

Фича до сих пор жила только в Mini App: ни джобы, ни хендлера в боте, сброс
неявный — в локальную полночь, по ключу quest_date = сегодня.

12:00 выбрано намеренно: остаётся полный день, чтобы забрать, и ни с чем
не пересекается (21:30 ключи, 22:10 усиление клуба, 22:15 энергия).
"""
from datetime import datetime, timedelta, date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from database.session import get_session
from database.models.character import Character
from database.models.daily_quest import DailyQuest
from database.models.reminder_character import ReminderCharacter
from services.daily_quest_service import DailyQuestService
from schedulers.scheduler_idle_training import DORMANT_AFTER
from logging_config import logger
from utils.notify import notify


class DailyGiftReminder:
    TEXT = (
        "🎁 Тебе чекає щоденний подарунок!\n\n"
        "Монети та енергія — забирай, поки день не закінчився. ⏳"
    )

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        self.scheduler.add_job(
            func=self.remind,
            trigger=CronTrigger(hour=12, minute=0),
            misfire_grace_time=3600,
        )
        self.scheduler.start()

    async def remind(self):
        now = datetime.now()
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(Character)
                    .join(ReminderCharacter, ReminderCharacter.character_id == Character.id)
                    # LEFT JOIN: в полдень у большинства строки на сегодня ещё нет,
                    # и такие игроки тоже должны попасть в выборку.
                    .outerjoin(
                        DailyQuest,
                        (DailyQuest.character_id == Character.id)
                        & (DailyQuest.quest_date == date.today()),
                    )
                    .where(
                        Character.is_bot == False,
                        Character.is_blocked == False,
                        Character.characters_user_id.isnot(None),
                        (DailyQuest.id.is_(None)) | (DailyQuest.gift_claimed.is_(False)),
                        ReminderCharacter.last_training_at.isnot(None),
                        ReminderCharacter.last_training_at >= now - DORMANT_AFTER,
                    )
                )
                characters = list(result.unique().scalars().all())

        # ponytail: claim_gift_notification создаёт строку daily_quests на каждого
        # уведомлённого. Ограничено 30-дневным окном активности.
        # Upgrade path: чистить строки старше 90 дней.
        sent = 0
        for character in characters:
            if not await DailyQuestService.claim_gift_notification(character.id):
                continue
            if await notify(
                character,
                self.TEXT,
                screen="home",
                button_text="🎁 Забрати подарунок",
            ):
                sent += 1
        logger.info(f"Daily gift reminder: sent {sent} of {len(characters)} candidates")
