from aiogram.filters.state import State, StatesGroup

class CreateCharacterState(StatesGroup):
    send_name    = State()
    set_gender      = State()
    set_position = State()