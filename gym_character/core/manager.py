from asyncio import Task
from services.reminder_character_service import RemniderCharacterService


class GymCharacterManager:

    tasks_jym: dict[int, Task] = {}

    @classmethod
    def add_gym_task(
        cls,
        character_id: int,
        task: Task,
    ) -> None:
        cls.tasks_jym[character_id] = task
        
    @classmethod
    async def remove_gym_task(
        cls,
        character_id: int,
    ) -> None:
        if not character_id in cls.tasks_jym:
            return    
        del cls.tasks_jym[character_id]
        await RemniderCharacterService.anulate_character_training_status(character_id)
        await RemniderCharacterService.anulate_training_character(character_id)