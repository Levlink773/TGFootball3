from aiogram.filters.callback_data import CallbackData
from constants import PositionCharacter

class SelectPosition(CallbackData, prefix="select_position"):
    position: PositionCharacter
