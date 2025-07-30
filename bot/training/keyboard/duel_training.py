from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.training.callbacks.training_callbacks import (
    SelectAngleTrainingDuel,
    NextStage
)
from training.duel.types import PositionAngle
from training.types import Stage

def select_position_angle(
    duel_id: str,
    end_time_health: int    
):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text = "⬆️ Вверх"  , 
                    callback_data=SelectAngleTrainingDuel(
                        angle=PositionAngle.UP, 
                        duel_id=duel_id,
                        end_time_health = end_time_health
                    )
    )
    keyboard.button(text = "⬅️ Вліво"  , 
                    callback_data=SelectAngleTrainingDuel(
                        angle=PositionAngle.LEFT, 
                        duel_id=duel_id,
                        end_time_health = end_time_health
                    )
    )
    
    keyboard.button(text = "➡️ Вправо"  , 
                    callback_data=SelectAngleTrainingDuel(
                        angle=PositionAngle.RIGHT, 
                        duel_id=duel_id,
                        end_time_health = end_time_health
                    )
    )
    
    return keyboard.adjust(1,2).as_markup()

def end_duel_training(
    end_time_health: int,
    count_score: int,
    next_stage: Stage
):
    return (
        InlineKeyboardBuilder()
        .button(text = "Завершити тренування"  ,
                callback_data=NextStage(
                    end_time_health = end_time_health,
                    count_score = count_score,
                    next_stage = next_stage
                )
        )
        .as_markup()
    )