import asyncio

from aiogram.types import Message

from database.models.user_bot import STATUS_USER_REGISTER
from database.models.character import Character

from bot.routers.register_user.config import (
    PHOTO_STAGE_REGISTER_USER,
    TEXT_STAGE_REGISTER_USER
)
from bot.routers.register_user.routers.join_to_training import join_to_training

from services.user_service import UserService


async def territory_academy(
    character: Character,
    message: Message
) -> None:
    await asyncio.sleep(5)
    new_status = STATUS_USER_REGISTER.TERRITORY_ACADEMY
    await UserService.edit_status_register(
        user_id=character.characters_user_id,
        status=new_status
    )
    await message.answer_photo(
        photo=PHOTO_STAGE_REGISTER_USER[new_status],
        caption=TEXT_STAGE_REGISTER_USER[new_status]
    )

