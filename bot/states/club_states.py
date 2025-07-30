from aiogram.filters.state import State, StatesGroup

class CreateClub(StatesGroup):
    send_name    = State()

class ChangeClubChatLink(StatesGroup):
    send_chat_link = State()
    
class FindClub(StatesGroup):
    send_name_club = State()
    view_clubs = State()
    
class SendMessageMembers(StatesGroup):
    send_message_members = State()
    
class SendCustomNameStadion(StatesGroup):
    send_name = State()
    
class EditDescriptionClub(StatesGroup):
    send_new_description = State()