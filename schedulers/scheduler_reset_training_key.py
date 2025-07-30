import asyncio
from datetime import datetime, timedelta

from aiogram import Bot

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database.models.character import Character

from services.character_service import CharacterService
from services.training_service import TrainingService

from utils.rate_limitter import rate_limiter

from loader import bot

class ResetTrainingKeyScheduler():
    _bot:Bot = bot
    TEMPLATE_TEXT_RESET_TRAINING_KEY = """
🎉 <b>Вітаємо!</b> 🔑  

Тобі видано <b>ключі для тренувань</b>!  
Тепер ти зможеш взяти участь у тренуванні завтра. ⚽🏆  

⏳ Не пропусти свій шанс покращити навички та стати сильнішим!  
"""

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()    
        self.send_queue = asyncio.Queue()

        
    async def reset_training_key(self) -> None:
        all_characters = await TrainingService.get_characters_how_not_have_key()
        await TrainingService.reset_training_keys()
        for character in all_characters:
            await self.send_queue.put(character)
        asyncio.create_task(self._send_messages())
        
    async def _send_messages(self) -> None:
        while not self.send_queue.empty():
            character = await self.send_queue.get()
            await self.__send_message(character)
        
    @rate_limiter
    async def __send_message(self, character: Character) -> None:
        try:
            await self._bot.send_message(
                chat_id=character.characters_user_id,
                text=self.TEMPLATE_TEXT_RESET_TRAINING_KEY
            )
        except Exception as E:
            print(E)
            pass  

    async def start(self):
        # await self.reset_training_key()
        self.scheduler.add_job(
            func=self.reset_training_key,
            trigger=CronTrigger(hour=21, minute=30),
            misfire_grace_time=10
        )
        self.scheduler.start()
