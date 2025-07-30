from datetime import datetime

from typing import Dict
from training.duel.duel_manager import DuelManager

from services.training_service import TrainingService   

from training.constans import TIME_REGISTER_TRAINING
from .training import Training
from .end_training import EndTraining

from logging_config import logger

class TrainingManager:
    _trainings: Dict[int, Training] = {}

    @classmethod
    def get_or_create_training(
        cls, 
        user_id: int, 
        character_id: int,
        range_training_times: list[datetime, datetime]
    ) -> Training:
        
        if user_id not in cls._trainings:
            cls._trainings[user_id] = Training(
                user_id      = user_id, 
                character_id = character_id,
                range_training_times = range_training_times
            )
        return cls._trainings[user_id]

    @classmethod
    def get_training(cls, user_id: int) -> Training:
        return cls._trainings.get(user_id, None)


    @classmethod
    async def start_training(cls, range_training_times: list[datetime, datetime]) -> None:
        time_start_register = range_training_times[0] - TIME_REGISTER_TRAINING
        time_end_register = range_training_times[1]
        joined_users = await TrainingService.get_joined_users(
            [time_start_register, time_end_register]
        )
        for user in joined_users:
            if user.user_id in cls._trainings:
                continue
            await cls.start_user_training(
                user_id      = user.user_id,
                character_id = user.character_id,
                range_training_times = range_training_times
            )
            
    @classmethod
    async def start_user_training(
        cls, 
        user_id: int, 
        character_id: int,
        range_training_times: list[datetime, datetime]
    ) -> None:
        try:
            training = cls.get_or_create_training(
                user_id = user_id, 
                character_id = character_id,
                range_training_times = range_training_times
            )
            await training.send_message_by_stage()
        except Exception as E:
            logger.error(f"Failed to start training for user {user_id}\nError: {E}")

    @classmethod
    async def end_all_trainings(cls) -> None:
        await DuelManager.end_all_duels()
        for _, training in cls._trainings.items():
            end_training = EndTraining(
                training = training
            )
            await end_training.end_training()
        cls._trainings.clear()
        
    @classmethod
    async def end_user_training(cls, user_id: int) -> None:
        if user_id in cls._trainings:
            end_training = EndTraining(
                training = cls._trainings[user_id]
            )
            await end_training.end_training()   
            del cls._trainings[user_id]
        
    