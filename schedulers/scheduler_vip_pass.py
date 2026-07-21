from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from bot.keyboards.vip_pass import (
    select_type_vip_pass
)

from database.models.character import Character

from services.vip_pass_service import VipPassService
from services.club_service import ClubService

from logging_config import logger
from loader import bot

from constants import END_VIP_PASS_PHOTO


class VipPassScheduler:
    """Manages VIP-pass expiry notifications using a single shared scheduler."""

    # Single shared scheduler for all VIP-pass jobs (avoids O(N) scheduler instances).
    _scheduler: AsyncIOScheduler = AsyncIOScheduler()

    TEXT_TEMPLATE = """
🔥 <b>Ваш VIP-пас закінчився!</b>

🎟️ Але не хвилюйтесь, адже у вас є шанс знову стати VIP-гравцем та отримати всі переваги:

✅ <i>🔋 300 енергії +150 щодня! Тепер 300 енергії замість 150 — більше можливостей для досягнення успіху!</i>
✅ <i>Х2 нагород з навчального центру — вдвічі більше корисних бонусів для твого прогресу!</i>
✅ <i>+5% успішності тренування — будь упевнений у своєму успіху і швидше досягай нових висот!</i>
✅ <i>VIP-статус — тепер твій нік буде виділятися, показуючи всім, хто тут справжній майстер гри!</i>

⚡ <b>Не втрачайте шанс бути на вершині!</b>
Продовжіть VIP-пас прямо зараз і отримуйте ще більше задоволення від гри!

"""

    def __init__(self, character: Character):
        self.character = character

        self._user_id: int = character.characters_user_id

        self._end_time: datetime = character.vip_pass_expiration_date

    async def _send_message(self):
        try:
            await bot.send_photo(
                chat_id      =self._user_id,
                photo        = END_VIP_PASS_PHOTO,
                caption      = self.TEXT_TEMPLATE,
                reply_markup = select_type_vip_pass()
            )
        except Exception as E:
            logger.error(f"Failed to send message to {self.character.name}\nError: {E}")

    def schedule_job(self):
        """Add (or replace) a VIP-expiry job on the shared scheduler."""
        job_id = f"end_time_vip_pass_{self._user_id}"
        self._scheduler.add_job(
            func=self._send_message,
            trigger=DateTrigger(run_date=self._end_time),
            id=job_id,
            name=job_id,
            misfire_grace_time=10,
            replace_existing=True,
        )

    @classmethod
    def ensure_started(cls):
        """Start the shared scheduler if it is not already running."""
        if not cls._scheduler.running:
            cls._scheduler.start()


class VipPassSchedulerService:
    def __init__(self):
        self._character_vip_pass_service = VipPassService()
        self._club_service = ClubService()

    async def start_timers(self):
        VipPassScheduler.ensure_started()
        characters = await self._character_vip_pass_service.get_have_vip_pass_characters()
        for character in characters:
            vip_pass_scheduler = VipPassScheduler(character)
            vip_pass_scheduler.schedule_job() 