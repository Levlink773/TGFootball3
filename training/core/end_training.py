import asyncio
from typing import Optional

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup

from bot.training.keyboard.select_stat import select_stat_from_update
from bot.training.keyboard.keyboard_re_invite import re_join_training

from database.models.character import Character

from services.training_service import TrainingService
from services.character_service import CharacterService

from loader import bot
from logging_config import logger

from training.utils.get_count_stats_by_score import calculate_stat, calculate_energy
from training.utils.text_stage import TEXT_TRAINING
from .training import Training


class EndTraining:
    _bot: Bot = bot

    def __init__(self, training: Training):
        self.training = training

    @property
    def count_stat(self):
        return calculate_stat(
            score = self.training.score,
        )

    @property
    def count_energy(self):
        return calculate_energy(
            score = self.training.score
        )

    async def end_training(self) -> None:
        try:
            await TrainingService.end_user_training(
                user_id = self.training.user_id
            )
            character: Character = await CharacterService.get_character_by_id(
                character_id = self.training.character_id
            )
            asyncio.create_task(self._send_reinvite_training(character))
            await CharacterService.edit_character_energy(
                character_id = character.id,
                amount_energy = self.count_energy
            )
            return await self.__send_message(
                text = TEXT_TRAINING.TRAINING_STATS_SELECTION.format(
                    stat_points = self.count_stat,
                    energy_points = self.count_energy
                ),
                keyboard = select_stat_from_update(self.count_stat)
            )
        except Exception as E:
            logger.error(f"Failed to end training\nError: {E}")
            
    async def __send_message(self, 
        text: str,
        keyboard: Optional[InlineKeyboardMarkup] = None 
    ):
        try:
            await self._bot.send_message(
                chat_id = self.training.user_id,
                text = text,
                reply_markup = keyboard
            )
        except Exception as E:
            logger.error(f"Failed to send message to {self.training.user_id}\nError: {E}")

    async def _send_reinvite_training(self, character: Character):
        await asyncio.sleep(5)
        await self.__send_message(
            text = TEXT_TRAINING.TRAINING_RE_INVITE.format(
                    count_key = character.training_key
                ),
            keyboard = re_join_training(
                character = character,
                end_time_health = self.training.end_time_from_keyboard
            )
        )