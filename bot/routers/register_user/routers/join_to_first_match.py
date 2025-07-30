from bot.keyboards.menu_keyboard import main_menu

from bot.routers.register_user.config import (
    TEXT_STAGE_REGISTER_USER
)

from database.models.user_bot import STATUS_USER_REGISTER
from database.models.character import Character

from services.user_service import UserService

from loader import bot


async def join_to_first_match_handler(character: Character) -> None:
    new_status = STATUS_USER_REGISTER.JOIN_FIRST_MATCH
    await UserService.edit_status_register(
        user_id=character.characters_user_id,
        status=new_status
    )
    user = await UserService.get_user(character.characters_user_id)
    await bot.send_message(
        chat_id=character.characters_user_id,
        text=TEXT_STAGE_REGISTER_USER[new_status],
        reply_markup=main_menu(user)
    )