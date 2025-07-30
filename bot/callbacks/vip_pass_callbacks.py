from aiogram.filters.callback_data import CallbackData
from bot.routers.stores.vip_pass.types import VipPassTypes

class SelectTypeVipPass(CallbackData, prefix="select_type_vip_pass"):
    type_vip_pass: VipPassTypes