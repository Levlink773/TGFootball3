from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    ReplyKeyboardBuilder
)

def create_character() -> ReplyKeyboardMarkup: 
    return (
        ReplyKeyboardBuilder()
        .button(
            text="СТВОРИТИ ПЕРСОНАЖА"
        )
        .as_markup(resize_keyboard=True)
    )