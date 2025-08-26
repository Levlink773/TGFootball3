from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database.models.character import Character
from services.character_service import CharacterService


class AnulateStatisticsScheduler:
    default_trigger_start = CronTrigger(hour=2)

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        self.scheduler.add_job(
            func=self._start,
            trigger=self.default_trigger_start,
            misfire_grace_time=10
        )
        self.scheduler.start()

    async def _start(self):
        # запускаем в 03:00
        self.scheduler.add_job(
            func=self.anulate_statistics,
            trigger=CronTrigger(hour=3),
            misfire_grace_time=10
        )

    async def anulate_statistics(self):
        characters: list[Character] = await CharacterService.get_all_characters_where_end_training()
        for ch in characters:
            # обнуляем статистику
            await CharacterService.anulate_statistics(ch.id)
            # генерируем новый tier_cipher
            await CharacterService.generate_new_tier_cipher(ch.id)