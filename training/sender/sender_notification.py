import asyncio
from datetime import datetime, timedelta

from aiogram import Bot

from database.models.character import Character
from services.character_service import CharacterService
from utils.rate_limitter import rate_limiter

from loader import bot
from logging_config import logger

from training.constans import (
    TIME_REGISTER_TRAINING,
    TIMERS_REGISTER_TRAINING,
    TIME_TRAINING,
    TIME_REGISTER_TRAINING
)
from training.utils.text_stage import TEXT_TRAINING


class NotificationSender:
    _bot: Bot = bot
    _preregister_time = int(TIME_REGISTER_TRAINING.total_seconds() // 60)
    _times_training = TIMERS_REGISTER_TRAINING
    
    _text_notification: str = TEXT_TRAINING.START_TRAINING_MESSAGE
    _text_template_time_training: str = TEXT_TRAINING.TEMPLATE_TEXT_TIME_TRAINING

    def __init__(self) -> None:
        self.send_queue = asyncio.Queue()
        
    def _get_text_timers_training(self) -> str:
        text = ""
        for time in self._times_training:
            start_time = datetime.strptime(time, "%H:%M") + TIME_REGISTER_TRAINING
            end_time = start_time + TIME_TRAINING

            text += self._text_template_time_training.format(
                start_time=start_time.strftime("%H:%M"),
                end_time=end_time.strftime("%H:%M")
            )

        return text
        
    
    async def send_notification(self):
        all_characters = await CharacterService.get_all_users_not_bot()
        for character in all_characters:
            await self.send_queue.put(character)

        asyncio.create_task(self._send_notification())
        
    async def _send_notification(self):
        while not self.send_queue.empty():
            character = await self.send_queue.get()
            await self.__send_message(character)
    
    
    @rate_limiter        
    async def __send_message(self, character: Character):
        try:
            await self._bot.send_message(
                chat_id=character.characters_user_id,
                text=self._text_notification.format(
                    text_times_training = self._get_text_timers_training(),
                    preregister_time = self._preregister_time
                ),
            )
        except Exception as E:
            logger.error(f"Failed to send message to {character.characters_user_id}\nError: {E}")