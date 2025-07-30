from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.keyboards.utils_keyboard import menu_plosha

def menu_statistic():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="📊 Команди в лігах")
    keyboard.button(text="📊 Таблиці ліг")
    keyboard.attach(menu_plosha())
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)
