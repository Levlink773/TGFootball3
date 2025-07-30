from aiogram.filters.callback_data import CallbackData

class SelectCountGetEnergy(CallbackData, prefix="select_get_energy"):
    count_energy: int