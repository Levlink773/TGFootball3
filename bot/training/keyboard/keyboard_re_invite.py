import random
import time

from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.training.callbacks.training_callbacks import JoinToTraining

from database.models.character import Character
from .buy_training_key import to_menu_buy_training_key

def re_join_training(
    character: Character,
    end_time_health: int
):
    if character.training_key:
        return join_to_training(end_time_health)
    else:
        return to_menu_buy_training_key()
    
def join_to_training(end_time_health: int):
    return (
        InlineKeyboardBuilder()
        .button(
            text="🎮 Приєднатися до тренування",
            callback_data=JoinToTraining(
                end_time_health = end_time_health
            )
        )
        .as_markup()
    )