from aiogram import Router, F
from aiogram.types import CallbackQuery

from constants_leagues import TypeLeague, config_top_20_club_league

from .statistic_matches import send_statisitcs_matches
from ...keyboard.menu_match_statistic import (
    select_type_matches_best_league, 
)
from ...callbacks.match_statistic_callbacks import (
    SelectTypeMatchLeague,
    SelectTypeMatchTop20League
)

menu_choice_type_top_20_group_router = Router()

@menu_choice_type_top_20_group_router.callback_query(
    SelectTypeMatchLeague.filter(
        F.type_league.is_(TypeLeague.TOP_20_CLUB_LEAGUE)
    )
)
async def select_type_league_statistic_matches(
    query: CallbackQuery,
):
    await query.message.edit_text(
        text="Виберіть групу",
        reply_markup=select_type_matches_best_league()
    )
    
    
@menu_choice_type_top_20_group_router.callback_query(
    SelectTypeMatchTop20League.filter()
)
async def select_group_statistic_matches(
    query: CallbackQuery,
    callback_data: SelectTypeMatchTop20League,
):
    if not config_top_20_club_league.league_is_active:
        date_state_league = config_top_20_club_league.DATETIME_START_LEAGUE.strftime("%d.%m.%Y")
        end_time_league = config_top_20_club_league.DATETIME_END_LEAGUE.strftime("%d.%m.%Y")
        text = (
            "<b>⚠️ Матчі цієї ліги ще не почалися!</b>\n\n"
            f"📅 Початок: <b>{date_state_league}</b>\n"
            f"🏁 Завершення: <b>{end_time_league}</b>\n\n"
            "Слідкуй за оновленнями, щоби не пропустити старт!"
        )
        return await query.message.answer(
            text=text
        )
    await send_statisitcs_matches(
        query=query,
        group_id=callback_data.type_group,
    )
