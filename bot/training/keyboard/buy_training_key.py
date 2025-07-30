from aiogram.utils.keyboard import InlineKeyboardBuilder


def buy_training_key(url_payement):
    return (
        InlineKeyboardBuilder()
        .button(text="Купити ключ для тренування", url=url_payement)
        .as_markup()
    )
    
    
def to_menu_buy_training_key():
    return (
        InlineKeyboardBuilder()
        .button(text="Придбати ключ", callback_data="buy_training_key")
        .as_markup()
    )