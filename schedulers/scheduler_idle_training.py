"""Daily nudge for players whose training is idle (Max 23.07).

Fires once a day and messages every non-bot character that has enough energy
to train but isn't currently training. Intentionally NOT a promo broadcast —
it only pings genuinely-idle players, gated on a real energy threshold.
"""
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from database.session import get_session
from database.models.character import Character
from database.models.reminder_character import ReminderCharacter
from loader import bot
from logging_config import logger
from utils.rate_limitter import rate_limiter

# Cheapest training (30 хв) costs 10 energy — no point nudging below that.
MIN_ENERGY_TO_NUDGE = 10


class IdleTrainingReminder:
    TEXT = (
        "💤 Твоє тренування не активне!\n\n"
        "Зайди в гру та почни тренування — прокачай гравця й отримай нагороди. ⚡"
    )

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        self.scheduler.add_job(
            func=self.remind_idle,
            trigger=CronTrigger(hour=18, minute=0),
            misfire_grace_time=600,
        )
        self.scheduler.start()

    async def remind_idle(self):
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(Character)
                    .join(ReminderCharacter, ReminderCharacter.character_id == Character.id)
                    .where(
                        Character.is_bot == False,
                        Character.characters_user_id.isnot(None),
                        Character.current_energy >= MIN_ENERGY_TO_NUDGE,
                        ReminderCharacter.character_in_training == False,
                    )
                )
                characters = result.scalars().all()
        for character in characters:
            await self._send(character)

    @rate_limiter
    async def _send(self, character: Character):
        try:
            await asyncio.sleep(1)
            await bot.send_message(chat_id=character.characters_user_id, text=self.TEXT)
        except Exception as e:
            logger.error(f"idle-training reminder failed for {character.characters_user_id}: {e}")
