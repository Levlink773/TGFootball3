from aiogram.filters.callback_data import CallbackData

class AdminSelectPvpDuel(CallbackData, prefix = "select_pvp"):
    pvp_duel_id: str