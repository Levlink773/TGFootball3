from aiogram.filters.callback_data import CallbackData
from constants import Gender, PositionCharacter

class SelectGender(CallbackData, prefix="select_gender"):
    gender: Gender
    
class SelectPositionCharacter(CallbackData, prefix="select_position"):
    position: PositionCharacter

class CreateCharacter(CallbackData, prefix="create_character"):
    gender: Gender
    position: PositionCharacter