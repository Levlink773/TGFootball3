from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove

from database.models.user_bot import UserBot, STATUS_USER_REGISTER

from constants import date_is_get_reward_christmas_tree

from ..callbacks.menu_callbacks import NextInstruction

ALL_MAIN_BUTTONS = [
    "⚽️ Матчі",
    "🖲 Тренування",
    "🗄 Тренувальна база",
    "🏃‍♂️ Мій футболіст",
    "👥 Команда",
    "🏬 Торговий квартал",
    "🏆 Зал слави",
    "📊 Статистика",
    "🗣 Cпілкування",
]

AVAILABLE_BUTTONS_BY_STATUS = {
    STATUS_USER_REGISTER.FIRST_TRAINING: ['🖲 Тренування'],
    STATUS_USER_REGISTER.BUY_EQUIPMENT: ['🏬 Торговий квартал'],
    STATUS_USER_REGISTER.TRAINING_CENTER: ['🗄 Тренувальна база'],
    STATUS_USER_REGISTER.END_TRAINING: ALL_MAIN_BUTTONS
}

def main_menu(user: UserBot):
    keyboard = ReplyKeyboardBuilder()
    if not user.characters:
        keyboard.button(text="⚽️ Створити персонажа")
    else:
        available_buttons = AVAILABLE_BUTTONS_BY_STATUS.get(user.status_register, [])
        for button_text in ALL_MAIN_BUTTONS:
            if button_text in available_buttons:
                if user.status_register != STATUS_USER_REGISTER.END_TRAINING:
                    final_text = f"✅ {button_text} ✅"
                else:
                    final_text = button_text
            else:
                final_text = f"🔒 {button_text}"

            keyboard.button(text=final_text)

    return keyboard.adjust(2).as_markup(resize_keyboard=True)
        
def menu_instruction(index_instruction: int):
    return (InlineKeyboardBuilder()
            .button(text = "➡️ Далі", callback_data=NextInstruction(index_instruction=index_instruction))
            .as_markup()
            )
    
def remove_keyboard():
    return ReplyKeyboardRemove(remove_keyboard=True)

def test():
    return ReplyKeyboardBuilder().button(text="TEST").as_markup(resize_keyboard = True, is_persistent=True, selective=True)
    