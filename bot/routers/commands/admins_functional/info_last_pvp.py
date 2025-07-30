import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database.models.character import Character
from database.models.duel import Duel

from bot.filters.check_admin_filter import CheckUserIsAdmin
from bot.keyboards.admins_keyboard import view_last_pvp_matches
from bot.callbacks.admins_callbacks import AdminSelectPvpDuel

from services.admins_functional_service import AdminFunctionalService
from services.duel_service import DuelService

from logging_config import logger

info_last_pvp_router = Router()


@info_last_pvp_router.message(
    Command("last_pvp"),
    CheckUserIsAdmin()
)
async def get_info_last_match(
    message: Message
):
    last_matches = await AdminFunctionalService.get_last_pvp_matches(
        count_matches=20
    )
    
    await message.answer(
        text = "Последние 20 пвп матечей",
        reply_markup = view_last_pvp_matches(
            matches = last_matches
        )
    )

@info_last_pvp_router.callback_query(
    AdminSelectPvpDuel.filter()
)
async def get_info_last_match(
    query: CallbackQuery,
    callback_data: AdminSelectPvpDuel
):
    match: Duel = await DuelService.get_duel_by_id(
        duel_id=callback_data.pvp_duel_id
    )
    if not match:
        return await query.answer(
            text = "Матч не найден"
        )
    text = get_text_duel(match)
    await query.message.answer(
        text
    )
    
def get_text_duel(duel: Duel):

    duel_time = duel.created_time.strftime("%d.%m.%Y %H:%M:%S")
    result_text = ""

    if duel.point_user_1 == duel.point_user_2:
        result_text = (
            f"Дуэль между {duel.user_1.name} и {duel.user_2.name} завершилась вничью. "
            f"Итоговый счет: {duel.point_user_1} : {duel.point_user_2}."
        )
    elif duel.point_user_1 > duel.point_user_2:
        result_text = (
            f"Дуэль между {duel.user_1.name} и {duel.user_2.name} завершилась победой {duel.user_1.name}. "
            f"Итоговый счет: {duel.point_user_1} : {duel.point_user_2}."
        )
    else:
        result_text = (
            f"Дуэль между {duel.user_1.name} и {duel.user_2.name} завершилась победой {duel.user_2.name}"
            f"Итоговый счет: {duel.point_user_1} : {duel.point_user_2}."
        )

    return (
        f"Отчет о дуэли:\n"
        f"Уникальный ID дуэли: {duel.duel_id}\n"
        f"Время проведения: {duel_time}\n"
        f"Участники: {duel.user_1.name} vs {duel.user_2.name}\n"
        f"Ставки: {duel.bit_user_1} vs {duel.bit_user_2}\n"
        f"{result_text}\n"
    )