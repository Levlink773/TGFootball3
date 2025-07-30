import asyncio
from bot.keyboards.menu_keyboard import main_menu

from bot.routers.register_user.config import (
    TEXT_STAGE_REGISTER_USER
)

from database.models.user_bot import STATUS_USER_REGISTER
from database.models.character import Character

from services.user_service import UserService

from loader import bot


async def claim_training_center_handler(character: Character) -> None:
    await bot.send_message(
        chat_id=character.characters_user_id,
        text="""
-<b>Вітаю, перший етап навчання позаду, твій гравець вже тренується</b>⚽️🏆 

<i>Залишилось ще трішки, ходімо далі</i>        
"""
    )
    await asyncio.sleep(3)
    new_status = STATUS_USER_REGISTER.TRAINING_CENTER
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