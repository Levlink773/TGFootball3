import logging

from aiogram import Bot
from aiogram.types import Message, CallbackQuery, ErrorEvent, User

from database.models.user_bot import UserBot

from typing import Any, Awaitable, Callable, Dict
from services.user_service import UserService

from loader import dp

async def get_user(user_bot: User) -> tuple[UserBot, bool]:
    try:
        user = await UserService.get_user(user_id=user_bot.id)
        if not user:
            await UserService.create_user(
                user_id = user_bot.id,
                user_name = user_bot.username,
                user_full_name = user_bot.full_name,
            )
            user = await UserService.get_user(user_id=user_bot.id)
        return user
    except Exception as E:
        logging.error(E)


@dp.error()
async def error_middleware(
    event: ErrorEvent,
    bot: Bot):
    logging.error("Critical error caused by %s", event.exception, exc_info=True)

@dp.callback_query.outer_middleware()
@dp.message.outer_middleware()
async def message_middleware(
    handler: Callable[[Message|CallbackQuery, Dict[str, Any]], Awaitable[Any]],
    event: Message|CallbackQuery,
    data: Dict[str, Any]
) -> Any:
    user  = await get_user(event.from_user)
    
    
    character = user.characters[0] if user.characters else []
    data.update({"user":user, "character":character})
    result = await handler(event, data)
    if isinstance(event, CallbackQuery):
        try:
            await event.answer()
        except:
            pass
    return result