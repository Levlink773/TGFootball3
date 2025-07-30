from datetime import datetime

from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder,
    InlineKeyboardBuilder
)
from bot.callbacks.hall_fame_callbacks import SelectHallFamePosition

from constants import DUEL_START_DAY_SEASON, DUEL_END_DAY_SEASON, PositionCharacter

from .utils_keyboard import menu_plosha



def menu_hall_fame():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text = "💪Рейтинг за силою гравця")
    keyboard.button(text = "👨‍👩‍👦‍👦 Рейтинг позицій")
    keyboard.button(text = "📊 Рейтинг за рівнем гравця")
    keyboard.button(text = "🏆 Рейтинг команд за силою")
    keyboard.button(text = "🏃🏼 Рейтинг бомбардирів")
    keyboard.button(text = "📊 Клубний рейтинг")
    keyboard.button(text = "👨‍👩‍👦‍👦 Рейтинг MVP")
    
    
    # if (datetime.now().day >= DUEL_START_DAY_SEASON) and (datetime.now().day <= DUEL_END_DAY_SEASON):
    #     keyboard.button(text = "👥 Рейтинг ПВП-пеналті") 
    
    keyboard.adjust(2, repeat=True)
    keyboard.attach(menu_plosha())    
    return keyboard.as_markup(resize_keyboard = True)
    
    
def select_position_rating():
    
    keyboard = InlineKeyboardBuilder()
    for position in PositionCharacter:
        
        keyboard.button(
            text = position.value,
            callback_data = SelectHallFamePosition(position = position)
        )
    return keyboard.adjust(1).as_markup()