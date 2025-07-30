from typing import Union

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from ...keyboard.menu_match_statistic import (
    select_type_league_matches, 
)

menu_choice_type_league_club_router = Router()

@menu_choice_type_league_club_router.message(
    F.text == "📊 Таблиці ліг"
)
@menu_choice_type_league_club_router.callback_query(
    F.data == "back_to_menu_select_statistic_matches"
)
async def menu_statistic_handler(
    evnt: Union[Message,CallbackQuery],
):
    if isinstance(evnt, CallbackQuery):
        func = evnt.message.edit_text
    else:
        func = evnt.answer
    
    await func(
                "Виберіть за якою лігою ви хочете переглянути матчі",
                reply_markup=select_type_league_matches()
            )