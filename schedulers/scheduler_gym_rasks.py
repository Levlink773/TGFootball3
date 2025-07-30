import asyncio
from aiogram.types import FSInputFile

from datetime import datetime, timedelta
from typing import Literal, Optional
from enum import Enum

from bot.club_infrastructure.types import InfrastructureType
from bot.club_infrastructure.config import INFRASTRUCTURE_BONUSES

from database.models.character import Character
from database.models.reminder_character import ReminderCharacter
from database.models.club_infrastructure import ClubInfrastructure

from services.character_service import CharacterService
from services.reminder_character_service import RemniderCharacterService
from services.club_infrastructure_service import ClubInfrastructureService

from constants import (
    X2_REWARD_WEEKEND_START_DAY,
    X2_REWARD_WEEKEND_END_DAY,
    chance_add_point, 
    const_name_characteristics,
    CHANCE_VIP_PASS
)
from utils.randomaizer import check_chance
from loader import bot
from logging_config import logger


class ResultTraining(Enum):
    SUCCESS = True
    FAILURE = False


class TrainingTextTemplate:
    SUCCESS_MESSAGE = "<b>Вітаю</b>! Параметр {characteristic} покращено на {points} поінта!"
    FAILURE_MESSAGE = "<b>На жаль</b>, ваш персонаж не зміг покращити {characteristic}. Спробуйте ще раз!"

    @staticmethod
    def get_training_text(result: ResultTraining, characteristic: str, points: int = 0) -> str:
        if result == ResultTraining.SUCCESS:
            return TrainingTextTemplate.SUCCESS_MESSAGE.format(characteristic=characteristic, points=points)
        return TrainingTextTemplate.FAILURE_MESSAGE.format(characteristic=characteristic)


class GymScheduler:

    def __init__(
        self,
        character: Character,
        type_characteristic: Literal['technique', 'kicks', 'ball_selection', 'speed', 'endurance'],
        time_training: timedelta,
        club_infrastructure: Optional[ClubInfrastructure] = None
    ) -> None:
        
        self.character= character
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
    
    

    def start_training(self) -> None:
        asyncio.create_task(
            self._wait_training(self.delta_time_training)
        )

    async def _wait_training(self, time_sleep: int) -> None:
        await asyncio.sleep(time_sleep)
        await self._run_training()

    async def _run_training(self) -> None:
        try:
            chance = chance_add_point[self.time_training]
            
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
            

class GymStartReseter:
    
    @classmethod
    async def start_iniatialization_gym(cls) -> None:
        all_character_in_gym: list[ReminderCharacter] = await RemniderCharacterService.get_characters_in_training()
        for character_rem in all_character_in_gym:
        
            if character_rem.character_in_training and character_rem.training_stats is None:
                await RemniderCharacterService.anulate_character_training_status(character_rem.character_id)
                await RemniderCharacterService.anulate_training_character(character_rem.character_id)
                continue
            
            character = await CharacterService.get_character_by_id(character_rem.character_id)
            if character.club_id:
                club_infrastructure = await ClubInfrastructureService.get_infrastructure(character.club_id)
            
            gym_scheduler = GymScheduler(
                character           = character,
                type_characteristic = character_rem.training_stats,
                time_training       = timedelta(seconds = character_rem.time_training_seconds),
                club_infrastructure = club_infrastructure
            )
            if cls.has_training_ended(character_rem, club_infrastructure):
                await gym_scheduler._run_training()
            else:
                asyncio.create_task(
                    gym_scheduler._wait_training(
                        cls.time_left(
                            character_rem=character_rem,
                            club_infrastructure=club_infrastructure 
                        )
                    )
            )

            
    @staticmethod
    def has_training_ended(
        character_rem: ReminderCharacter, 
        club_infrastructure: ClubInfrastructure
    ) -> bool:
        return GymStartReseter.time_left(character_rem, club_infrastructure) < 0
    
    @staticmethod
    def time_left(
        character_rem: ReminderCharacter,
        club_infrastructure: ClubInfrastructure
    ) -> timedelta:
        time_end = character_rem.time_start_training + timedelta(seconds=character_rem.time_training_seconds)
        
        if club_infrastructure:
            reduction_procent = INFRASTRUCTURE_BONUSES[InfrastructureType.SPORTS_MEDICINE].get(
                level=club_infrastructure.get_infrastructure_level(InfrastructureType.SPORTS_MEDICINE)
            )
            reduction_time = (character_rem.time_training_seconds * abs(reduction_procent)) // 100
            time_end: datetime = time_end - timedelta(seconds=reduction_time)
        
        return (time_end - datetime.now()).total_seconds()

    