from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.callbacks.bank_callbacks import (
    SelectTypeMoneyPack
)
from bot.routers.stores.bank.types import MoneyPackType, money_packs

def select_type_money_pack():
    keyboard = InlineKeyboardBuilder()
    for money_pack in MoneyPackType:
        current_pack = money_packs.get(money_pack)
        keyboard.button(
            text = f"{current_pack.name} [{current_pack.price} грн] [{current_pack.coins} 💵]",
            callback_data = SelectTypeMoneyPack(
                type_money_pack = money_pack
            )
        )
    keyboard.adjust(1)
    return keyboard.as_markup()

def buy_current_pack(url_payment: str):
    return (
        InlineKeyboardBuilder()
        .button(
            text = "Придбати",
            url  = url_payment
        )
        .as_markup()
    )