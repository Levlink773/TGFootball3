from aiogram.filters.state import State, StatesGroup

class RegisterUserState(StatesGroup):
    send_name = State()
    select_gender = State()
    
class JoinToClubState(StatesGroup):
    join_to_club = State()
    send_name_new_club = State()