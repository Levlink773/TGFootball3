from aiogram import Router, F
from aiogram.types import Message

block_uses_router = Router()


@block_uses_router.message(
    F.text.startswith("🔒")
)
async def block_users_handler(
    message: Message, 
):
    await message.answer(
        text = (
    "⛔️ <b>Функцію тимчасово заблоковано</b>\n\n"
    "🎓 Завершіть навчання, щоб отримати доступ до всіх можливостей гри. "
    "Пройдіть перші кроки та відкрийте весь ігровий світ!"
        )
    )