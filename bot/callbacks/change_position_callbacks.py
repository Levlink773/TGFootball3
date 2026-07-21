from aiogram.filters.callback_data import CallbackData
from constants import PositionCharacter

class SelectPosition(CallbackData, prefix="change_pos"):
    position: PositionCharacter
