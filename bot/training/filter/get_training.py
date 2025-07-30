from typing import Any
from aiogram.filters import BaseFilter

from database.models.character import Character
from training.core.manager_training import TrainingManager


class GetTraining(BaseFilter):
    
    async def __call__(self, *arg, **kwg) -> Any:
        character: Character = kwg.get("character", None)
        if not character:
            return False
        
        training = TrainingManager.get_training(
            user_id = character.characters_user_id
        )
        if not training:
            return False
    
        return {"training" : training}