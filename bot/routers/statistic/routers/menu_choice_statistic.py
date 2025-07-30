from aiogram import Router, F
from aiogram.types import Message

from bot.routers.statistic.keyboard.menu_statistic import menu_statistic

menu_statistic_router = Router()

@menu_statistic_router.message(
    F.text.regexp(r"(✅\s*)?📊 Статистика(\s*✅)?")
)
async def menu_choice_league_club_handler(
    message: Message,
):
    await message.answer(
        text = "Виберіть статистику по лігам, яку ви хочете переглянути.",
        reply_markup=menu_statistic()
    )