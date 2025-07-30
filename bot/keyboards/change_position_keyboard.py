from aiogram.utils.keyboard import InlineKeyboardBuilder
from constants import PositionCharacter
from bot.callbacks.change_position_callbacks import SelectPosition

def select_position(current_position: PositionCharacter):
    keyboard = InlineKeyboardBuilder()
    
    for position in PositionCharacter:
        if position == current_position:
            continue
        keyboard.button(
            text=position.value,
            callback_data=SelectPosition(
                position = position
            )
        )
    keyboard.adjust(1)
    return keyboard.as_markup()

def buy_change_position(
    url_payment: str,
    new_position_name: str    
):
    return (
        InlineKeyboardBuilder()
        .button(
            text=f"Змінити на {new_position_name}",
            url=url_payment
        )
        .as_markup()
    )
    