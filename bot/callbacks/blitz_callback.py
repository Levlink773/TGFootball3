from aiogram.filters.callback_data import CallbackData


class BlitzRegisterCallback(CallbackData, prefix="blitz_register"):
    blitz_id: int