from aiogram import Router, F
from aiogram.types import Message

locked_buttons_router = Router()


# Реєструється останнім у main_router: ловить натискання на 🔒-кнопки,
# які раніше мовчки ігнорувалися (текст кнопки не збігався з жодним хендлером).
@locked_buttons_router.message(F.text.startswith("🔒"))
async def locked_button_handler(message: Message):
    await message.answer("🔒 Цей розділ відкриється після завершення навчання")
