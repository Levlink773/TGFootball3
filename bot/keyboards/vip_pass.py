from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.callbacks.vip_pass_callbacks import SelectTypeVipPass
from bot.routers.stores.vip_pass.types import VipPassTypes

def select_type_vip_pass():
    return (
        InlineKeyboardBuilder()
        .button(
            text = "На 7 дней",
            callback_data = SelectTypeVipPass(
                type_vip_pass=VipPassTypes.seven_days_pass
            )
        )
        .button(
            text = "На 30 дней",
            callback_data = SelectTypeVipPass(
                type_vip_pass=VipPassTypes.month_pass
            )
        )
        .adjust(1)
        .as_markup()
    )

def buy_vip_pass(
    url_payment: str,
    duration: int
):
    return (
        InlineKeyboardBuilder()
        .button(
            text = f"Придбати VIP на {duration} днів",
            url = url_payment
        )

        .adjust(1)
        .as_markup()
    )