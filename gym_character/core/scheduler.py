import asyncio
from datetime import datetime, timedelta

from bot.club_infrastructure.types import InfrastructureType
from bot.club_infrastructure.config import INFRASTRUCTURE_BONUSES

from database.models.reminder_character import ReminderCharacter
from database.models.club_infrastructure import ClubInfrastructure

from services.character_service import CharacterService
from services.reminder_character_service import RemniderCharacterService
from services.club_infrastructure_service import ClubInfrastructureService

from .gym import Gym
from .manager import GymCharacterManager

class GymStartReseter:
    
    @classmethod
    async def start_iniatialization_gym(cls) -> None:
        all_character_in_gym: list[ReminderCharacter] = await RemniderCharacterService.get_characters_in_training()
        for character_rem in all_character_in_gym:
        
            if character_rem.character_in_training and character_rem.training_stats is None:
                await RemniderCharacterService.anulate_character_training_status(character_rem.character_id)
                await RemniderCharacterService.anulate_training_character(character_rem.character_id)
                continue
            
            club_infrastructure = None
            character = await CharacterService.get_character_by_id(character_rem.character_id)
            if character.club_id:
                club_infrastructure = await ClubInfrastructureService.get_infrastructure(character.club_id)
            
            gym_scheduler = Gym(
                character           = character,
                type_characteristic = character_rem.training_stats,
                time_training       = timedelta(seconds = character_rem.time_training_seconds),
                club_infrastructure = club_infrastructure
            )
            if cls.has_training_ended(character_rem, club_infrastructure):
                await gym_scheduler._run_training()
            else:
                task = asyncio.create_task(
                    gym_scheduler._wait_training(
                        cls.time_left(
                            character_rem=character_rem,
                            club_infrastructure=club_infrastructure 
                        )
                    )
                )
                GymCharacterManager.add_gym_task(
                    character_id = character_rem.character_id,
                    task = task
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
