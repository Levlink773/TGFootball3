import time

from typing import Any, Union
from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

from training.core.manager_training import TrainingManager

from bot.training.callbacks.training_callbacks import (
    JoinToTraining,
    QTECallback,
    NextStage
)

ApprovedCallbacks = Union[JoinToTraining, QTECallback, NextStage]

class TrainingIsActive(BaseFilter):
    
    async def __call__(self, query: CallbackQuery ,*arg, **kwg) -> Any:
        current_time = time.time()
        
        callback_data: ApprovedCallbacks = kwg.get('callback_data', None)
        if not callback_data:
            return False
        
        end_time_health = callback_data.end_time_health
        if end_time_health < current_time:
            await query.message.edit_reply_markup(reply_markup = None)
            return False
        return True