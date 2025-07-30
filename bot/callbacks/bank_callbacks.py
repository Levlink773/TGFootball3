from aiogram.filters.callback_data import CallbackData
from bot.routers.stores.bank.types import MoneyPackType

class SelectTypeMoneyPack(CallbackData, prefix="select_type_money_pack"):
    type_money_pack: MoneyPackType
