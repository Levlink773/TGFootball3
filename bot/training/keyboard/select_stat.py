from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.training.callbacks.training_callbacks import SelectStat
from constants import const_name_characteristics

def select_stat_from_update(count_stat: int):
    keyboard = InlineKeyboardBuilder()
    
    for stat, name_stat in const_name_characteristics.items():
        keyboard.button(
            text = name_stat,
            callback_data = SelectStat(
                stat = stat,
                count_stat = count_stat
            )
        )
    keyboard.adjust(1)
    return keyboard.as_markup()