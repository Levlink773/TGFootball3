from aiogram import Router, F
from aiogram.types import Message

from database.models.user_bot import UserBot
from bot.keyboards.training_base import menu_training_base


training_base_router = Router()

@training_base_router.message(
    F.text.regexp(r"(✅\s*)?🗄 Тренувальна база(\s*✅)?")
)
async def training_facilities_handler(
    message: Message,
    user: UserBot
):
    await message.answer(
        "Вітаю на тренувальній базі!", 
        reply_markup = menu_training_base(user)
    )