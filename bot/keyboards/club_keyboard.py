from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.club_infrastructure.callbacks.infrastructure_callbacks import SelectMenuInfrastructure

from database.models.club import Club
from database.models.character import Character

from .utils_keyboard import pagination_keyboard, menu_plosha
from ..callbacks.switcher import SwitchClub
from ..callbacks.club_callbacks import (
    SelectClubToJoin, 
    JoinToClub, 
    TransferOwner, 
    DeleteClub, 
    SelectSchema, 
    SelectClubToView, 
    ViewCharatcerClub,
    KickMember,
    SelectPhotoStadion,
    ApprovedPhotoStadion,
    InvoiceClubCallback
)
from constants import MAX_LEN_MEMBERS_CLUB, ITEM_PER_PAGE
from utils.club_shemas import SchemaClub 

def main_menu_club(character: Character):
    keybaord = ReplyKeyboardBuilder()
    if not character.club_id:
        keybaord.button(text = "⛩ Створити свою команду")
        keybaord.button(text = "🎮 Приєднатися до команди")
    else:
        keybaord.button(text = "👥 Моя команда")
        keybaord.button(text = "🧿 Переглянути інші команди")
        
    keybaord.attach(menu_plosha())
    return keybaord.adjust(1).as_markup(resize_keyboard = True)
        
    
def club_menu_keyboard(club: Club, character: Character):
    keyboard = InlineKeyboardBuilder()
    _character_is_owner: bool = club.owner_id == character.characters_user_id
    _text_only_invoice: str = "✅" if club.is_invite_only else "❌"
    
    if _character_is_owner:
        if not club.link_to_chat:
            keyboard.button(text="⚙️ Додати посилання на чат команди",  callback_data="change_club_chat")
        else:
            keyboard.button(text="⚙️ змінити посилання на чат команди", callback_data="change_club_chat")
        keyboard.button(text = "🔄 Змінити схему команди", callback_data="change_schema_club")
        keyboard.button(text = "⌨️ Надіслати повідомлення всьому команди", callback_data="send_message_all_member_club")
        keyboard.button(text = "🫂 Передати права на команду", callback_data="transfer_rights")
        keyboard.button(text = "❌ Видалити мій команду", callback_data="delete_my_club")
        keyboard.button(text = "🦶👤 Вигнати користувача", callback_data="kick_user")
        keyboard.button(text = "🏟 Налаштування виду стадіона", callback_data="custom_stadion")
        keyboard.button(text = "📝 Опис команди", callback_data="description_club")
        keyboard.button(text = f"👞 Тільки за запитами: {_text_only_invoice}", callback_data="only_is_approved")
    else:
        keyboard.button(text = "🎮 Схема команди", callback_data="view_schema_club")
        keyboard.button(text = "⬅️ Вийти з команди", callback_data="leave_club")
    keyboard.button(text="👥 Користувачі команди",callback_data=ViewCharatcerClub(club_id=club.id))
    keyboard.button(
        text = "🏢 Инфраструктура клуба", 
        callback_data = SelectMenuInfrastructure(
            character_is_owner = _character_is_owner
        )
    )
    
    return keyboard.adjust(1, repeat=True).as_markup()


def register_join_club():
    return (
        InlineKeyboardBuilder()
        .button(text="🕹 Приєднатися до команди", callback_data="join_club_new_member")
        .button(text="⛩ Створити свою команду", callback_data="create_club_new_member")
        .adjust(1, repeat=True)
        .as_markup()
    )
            


def find_club(all_clubs: list[Club], page: int = 0 ):
    keyboard = InlineKeyboardBuilder()
    
    start = page * ITEM_PER_PAGE
    end = start + ITEM_PER_PAGE
    
    all_clubs = sorted(all_clubs, key=lambda club: club.total_power, reverse=True)

    keyboard.attach(pagination_keyboard(
        total_items  = len(all_clubs), 
        current_page = page, 
        switcher     = SwitchClub))
    
    
    for club in all_clubs[start:end]:
        text_club = "⚽ {name_club} [{current_len_members}/{all_len_members}][Сила {power_club}]".format(
            name_club = club.name_club,
            current_len_members = len(club.characters),
            all_len_members = MAX_LEN_MEMBERS_CLUB,
            power_club = int(club.total_power)
        )
        
        keyboard.button(text=text_club, callback_data=SelectClubToJoin(club_id=club.id))
    keyboard.adjust(3,*([1]*10))
    return keyboard.as_markup()


def view_club(all_clubs: list[Club], page: int):
    keyboard = InlineKeyboardBuilder()
    all_clubs = sorted(all_clubs, key=lambda club: club.total_power, reverse=True)

    start = page * ITEM_PER_PAGE
    end = start + ITEM_PER_PAGE
     
    keyboard.attach(pagination_keyboard(
        total_items  = len(all_clubs), 
        current_page = page, 
        switcher     = SwitchClub
                                        )
                    )
    
    
    for club in all_clubs[start:end]:
        text_club = "⚽ {name_club} [{current_len_members}/{all_len_members}][Сила {power_club}]".format(
            name_club = club.name_club,
            current_len_members = len(club.characters),
            all_len_members = MAX_LEN_MEMBERS_CLUB,
            power_club = int(club.total_power)
        )
        
        keyboard.button(text=text_club, callback_data=SelectClubToView(club_id=club.id))
    keyboard.adjust(3,*([1]*10))
    return keyboard.as_markup()
    
def view_character_club(club_id: int):
    return (InlineKeyboardBuilder()
            .button(text="👥 Користувачі команди",callback_data=ViewCharatcerClub(club_id=club_id))
            .adjust(1)
            .as_markup()
            )


def join_to_club_keyboard(club_id: int):
    return (InlineKeyboardBuilder()
            .button(text = "➕ Приєднатися до команди", callback_data=JoinToClub(club_id=club_id))
            .as_markup())
    
def transfer_club_owner_keyboard(club: Club):
    keyboard = InlineKeyboardBuilder()
    for character_club in club.characters:
        if club.owner_id == character_club.characters_user_id:
            continue
        
        keyboard.button(text = f"{character_club.character_name}",
                        callback_data=TransferOwner(user_id_new_owner =  character_club.characters_user_id))
    keyboard.adjust(3)
    return keyboard.as_markup()


def definitely_delete_club_keyboard(club_id: int):
    return (InlineKeyboardBuilder()
            .button(text = "Точно видалити моб команду?", callback_data=DeleteClub(club_id=club_id))
            .as_markup()
            )
    
def select_schema_keyboard():
    keyboard = InlineKeyboardBuilder()
    for num_schema in range(1,6):
        
        info_schema = SchemaClub.__getattribute__(SchemaClub, f"sсhema_{num_schema}")
        text_shema = "-".join(map(str, list(info_schema.values())[:-1]))
        keyboard.button(
            text=f"Cхема [{text_shema}]",
            callback_data=SelectSchema(select_schema = f"sсhema_{num_schema}")
        )
    keyboard.adjust(2)
    return keyboard.as_markup()

def select_user_kick(members_club: list[Character]):
    keyboard = InlineKeyboardBuilder()
    for member in members_club:
        keyboard.button(text = f"Вигнати {member.character_name}", 
                        callback_data=KickMember(
                            character_id=member.id
                        ))
        
    return keyboard.adjust(1).as_markup()


def select_option_custom_stadion():
    return (InlineKeyboardBuilder()
            .button(text = "Назва стадіону", 
                    callback_data = "select_custom_stadion_name")
            .button(text = "Фото стадіону",
                    callback_data = "select_custom_stadion_photo"
                    )
            .adjust(1)
            .as_markup()
            )

def menu_photo_custom_stadion():
    keyboard = InlineKeyboardBuilder()
    for num in range(1,10):
        patch_to_photo = f"src/club_stadions/stadion_{num}.jpg"
        keyboard.button(
            text = f"Фото {num}",
            callback_data = SelectPhotoStadion(
                patch_to_photo = patch_to_photo
            )
        )
    keyboard.adjust(2)
    return keyboard.as_markup()

def aproved_photo_stadion(patch_to_photo: str):
    return (
        InlineKeyboardBuilder()
        .button(text = "Вибрати дане фото", 
                callback_data = ApprovedPhotoStadion(
                    patch_to_photo = patch_to_photo
                ))
        .as_markup()
    )
    
def send_invite_to_join_club(
    club_id: int,
    character_id: int
) -> InlineKeyboardBuilder:
    return (
        InlineKeyboardBuilder()
        .button(
            text = "✅ Принять игрока в команду",
            callback_data = InvoiceClubCallback(
                club_id = club_id,
                character_id = character_id,
                is_approved = True
            )
        )
        .button(
            text = "❌ Відхилити заявку",
            callback_data = InvoiceClubCallback(
                club_id = club_id,
                character_id = character_id,
                is_approved = False
            )
        )
        .adjust(1)
        .as_markup()
    )
