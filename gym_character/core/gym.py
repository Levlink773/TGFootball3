import asyncio
from asyncio import Task

from datetime import datetime, timedelta
from typing import Optional

from aiogram import Bot
from aiogram.types import FSInputFile

from bot.club_infrastructure.types import InfrastructureType
from bot.club_infrastructure.config import INFRASTRUCTURE_BONUSES

from constants import (
    X2_REWARD_WEEKEND_START_DAY,
    X2_REWARD_WEEKEND_END_DAY,
    chance_add_point, 
    const_name_characteristics,
    CHANCE_VIP_PASS
)

from database.models.character import Character
from database.models.club_infrastructure import ClubInfrastructure

from services.character_service import CharacterService
from services.reminder_character_service import RemniderCharacterService

from utils.randomaizer import check_chance
from logging_config import logger
from loader import bot

from gym_character.types import TypeCharacteristic, ResultTraining
from gym_character.templates import TrainingTextTemplate

from .manager import GymCharacterManager

class Gym:
    
    _bot: Bot = bot
    
    def __init__(
        self,
        character: Character,
        type_characteristic: TypeCharacteristic,
        time_training: timedelta,
        club_infrastructure: Optional[ClubInfrastructure] = None
    ) -> None:
        self.character = character
        self.type_characteristic = type_characteristic
        self.time_training = time_training
        self.club_infrastructure = club_infrastructure
        
        self.result_training: ResultTraining = None
        
    @property
    def training_points(self) -> int:
        today = datetime.now().day
        is_weekend = X2_REWARD_WEEKEND_START_DAY <= today <= X2_REWARD_WEEKEND_END_DAY
        return 2 if is_weekend else 1

    @property
    def delta_time_training(self) -> int:
        reduction_procent = INFRASTRUCTURE_BONUSES[InfrastructureType.SPORTS_MEDICINE].get(
            level = self.club_infrastructure.get_infrastructure_level(InfrastructureType.SPORTS_MEDICINE)
        )
        reduction_time = (self.time_training.total_seconds() * abs(reduction_procent)) // 100
        return self.time_training.total_seconds() - reduction_time
    
    
    def start_training(self) -> Task:
        task_training = asyncio.create_task(
            self._wait_training(self.delta_time_training)
        )
        return task_training
    
    async def _wait_training(self, time_sleep: int) -> None:
        await asyncio.sleep(time_sleep)
        await self._run_training()
        
    async def _wait_training(self, time_sleep: int) -> None:
        try:
            await asyncio.sleep(time_sleep)
            await self._run_training()
        except asyncio.CancelledError:
            await RemniderCharacterService.anulate_character_training_status(self.character.id)
            await RemniderCharacterService.anulate_training_character(self.character.id)
            
    async def _run_training(self) -> None:
        try:
            chance = chance_add_point[self.time_training]
            
            if not await RemniderCharacterService.character_in_training(
                character_id=self.character.id
            ):
                raise ValueError("Персонаж не в тренуванні")
            
            if self.character.vip_pass_is_active:
                chance += CHANCE_VIP_PASS
                
            if self.club_infrastructure:
                infrastructure_bonus = INFRASTRUCTURE_BONUSES[InfrastructureType.TRAINING_BASE].get(
                    level = self.club_infrastructure.get_infrastructure_level(InfrastructureType.TRAINING_BASE)
                )
                chance += infrastructure_bonus
                
            success = check_chance(chance)
            self.result_training = ResultTraining.SUCCESS if success else ResultTraining.FAILURE

            if self.result_training == ResultTraining.SUCCESS:
                await CharacterService.update_character_characteristic(
                    character_id=self.character.id,
                    type_characteristic=self.type_characteristic,
                    amount_add_points=self.training_points
                )
                
            await self.send_end_training_message()
            await GymCharacterManager.remove_gym_task(self.character.id)
        except Exception as e:
            logger.error(f"Ошибка при выполнении тренировки: {e}")
        finally:
            await RemniderCharacterService.anulate_character_training_status(self.character.id)
            await RemniderCharacterService.anulate_training_character(self.character.id)

    async def send_end_training_message(self) -> None:
        try:
            if not self.character:
                raise ValueError("Персонаж не найден для отправки сообщения")

            if self.result_training is None:
                raise ValueError("Результат тренировки не определён")

            characteristic_name = const_name_characteristics[self.type_characteristic]
            points = self.training_points if self.result_training == ResultTraining.SUCCESS else 0
            
            message_text = TrainingTextTemplate.get_training_text(self.result_training, characteristic_name, points)
            
            photo_path = f"src/{'success' if self.result_training == ResultTraining.SUCCESS else 'failure'}_training.jpg"
            photo = FSInputFile(photo_path)

            await bot.send_photo(
                chat_id=self.character.characters_user_id,
                photo=photo,
                caption=message_text
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю {self.character.character_name}: {e}")
            