from aiogram.filters.callback_data import CallbackData
from datetime import timedelta

class SelectGymType(CallbackData, prefix="select_gym_type"):
    gym_type: str
    new_user: bool = False
    
class SelectTimeGym(CallbackData, prefix="select_time_gym"):
    gym_time: timedelta
    gym_type: str
    
class SelectCountDonateEnergy(CallbackData, prefix = "select_donate_energy"):
    count_energy: int
    club_id: int