from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database.models.user_bot import (
    UserBot,
    STATUS_USER_REGISTER
)

from .utils_keyboard import menu_plosha

ALL_TRAINING_BUTTONS = [
    "🖲 Тренування",
    "👨🏻‍🏫 Тренування з тренером",
    "🏫 Навчальний центр",
    "💪🏻 Посилення команди",
    "🏪🔋 Крамниця енергії"
]

AVAILABLE_BUTTONS_BY_STATUS = {
    STATUS_USER_REGISTER.TRAINING_CENTER: ['🏫 Навчальний центр'],
    STATUS_USER_REGISTER.END_TRAINING: ALL_TRAINING_BUTTONS
}


def menu_training_base(user: UserBot):
    builder = ReplyKeyboardBuilder()
    available_buttons = AVAILABLE_BUTTONS_BY_STATUS.get(user.status_register, [])
    for button_text in ALL_TRAINING_BUTTONS:
        if button_text in available_buttons:
            if user.status_register != STATUS_USER_REGISTER.END_TRAINING:
                final_text = f"✅ {button_text} ✅"
            else:
                final_text = button_text
        else:
            final_text = f"🔒 {button_text}"

        builder.button(text=final_text)
    builder.attach(menu_plosha())
    return builder.adjust(2).as_markup(resize_keyboard=True)

