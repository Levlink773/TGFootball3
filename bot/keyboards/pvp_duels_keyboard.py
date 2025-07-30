from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.callbacks.pvp_duel_callbacks import (
    SelectEnergyBit,
    SelectPositionAngle)

from pvp_duels.types import PositionAngle

from constants import ALL_COUNT_ENERGY_BIT


def find_oponent_user_duel():
    return (
        InlineKeyboardBuilder()
        .button(text = "Знайти суперника 🎯", callback_data="find_enemy_duel")
        .as_markup()
    )
    
def leave_pool_find_oponent():
    return (
        InlineKeyboardBuilder()
        .button(text= "🚫 Зупинити пошук суперника", callback_data="leave_pool_find_oponent")
        .as_markup()
    )
    
def select_bit(duel_id: str):
    keyboard = InlineKeyboardBuilder()
    
    for count_energy_bit in ALL_COUNT_ENERGY_BIT:
        keyboard.button(
            text=f"Поставити 🔋 {count_energy_bit}",
            callback_data=SelectEnergyBit(
                count_energy=count_energy_bit,
                duel_id=duel_id
                )
        )
    return keyboard.adjust(1).as_markup()

def select_position_angle(duel_id: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text = "⬆️ Вверх"  , 
                    callback_data=SelectPositionAngle(
                        position_angle=PositionAngle.UP, duel_id=duel_id)
                    )
    keyboard.button(text = "⬅️ Вліво"  , 
                    callback_data=SelectPositionAngle(
                        position_angle=PositionAngle.LEFT, duel_id=duel_id)
                    )
    
    keyboard.button(text = "➡️ Вправо"  , 
                    callback_data=SelectPositionAngle(
                        position_angle=PositionAngle.RIGHT, duel_id=duel_id)
                    )
    
    return keyboard.adjust(1,2).as_markup()