import random
import time

from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.training.callbacks.training_callbacks import QTECallback

from training.constans import DIRECTIONS

def get_qte_keyboard(
    correct_direction: str,
    end_time_health: int,
    shuffle: bool = False,
    stage: int = 1
):
    timestamp = float(time.time())

    directions = DIRECTIONS[:]
    if shuffle:
        random.shuffle(directions)
    directions.insert(4, "#️⃣")
    keyboard = InlineKeyboardBuilder()
    for direction in directions:
        callback = QTECallback(
            direction = direction,
            correct_direction=correct_direction,
            stage = stage,
            timestamp = timestamp,
            end_time_health = end_time_health
        )
        keyboard.button(text=direction, callback_data=callback)
    keyboard.adjust(3)
    return keyboard.as_markup()