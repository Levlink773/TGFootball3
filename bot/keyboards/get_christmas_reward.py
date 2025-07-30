from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_christmas_reward_keyboard():
    return (
        InlineKeyboardBuilder()
        .button(text = "🎁 Отримати подарунок",
                callback_data = "get_christmas_reward")
        .adjust(1)
        .as_markup()
    )