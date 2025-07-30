from aiogram.filters.callback_data import CallbackData

from constants import PositionCharacter

class SelectHallFamePosition(CallbackData, prefix="select_hall_fame_position"):
    position: PositionCharacter