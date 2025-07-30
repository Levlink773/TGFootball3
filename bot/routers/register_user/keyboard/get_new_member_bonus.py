from aiogram.types import InlineKeyboardMarkup

from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_box_new_member() -> InlineKeyboardMarkup:
    return (
        InlineKeyboardBuilder()
        .button(
            text = "🗃 Получити кейс",
            callback_data = "open_box_new_member"
        )
        .as_markup()
    )