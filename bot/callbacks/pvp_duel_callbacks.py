from aiogram.filters.callback_data import CallbackData
from pvp_duels.types import PositionAngle

class SelectEnergyBit(CallbackData, prefix="select_bit"):
    count_energy: int
    duel_id: str
    
class SelectPositionAngle(CallbackData, prefix = "select_angle"):
    position_angle: PositionAngle
    duel_id: str