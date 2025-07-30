from typing import Optional
from aiogram.filters import BaseFilter

from bot.training.callbacks.training_callbacks import (
    SelectAngleTrainingDuel
)
from training.duel.duel_manager import DuelManager
from training.duel.types import DuelData

class GetDuelData(BaseFilter):
    
    async def __call__(self, *arg, **kwg) -> Optional[dict[str, DuelData]]:
        callback_data: SelectAngleTrainingDuel = kwg.get('callback_data', None)
        if not callback_data:
            return None
        
        duel_data = DuelManager.get_duel(
            duel_id= callback_data.duel_id
        ).duel_data
        if not duel_data:
            return None
    
        return {"duel_data" : duel_data}