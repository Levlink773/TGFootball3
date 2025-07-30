from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.models.character import Character

from constants_leagues import GetConfig, TypeLeague

from services.league_services.league_service import LeagueService

from ...callbacks.match_statistic_callbacks import SelectTypeMatchLeague
from ...keyboard.menu_match_statistic import (
    select_type_league_matches, 
    select_group
)


menu_select_type_group_router = Router()

@menu_select_type_group_router.callback_query(
    SelectTypeMatchLeague.filter(
        F.type_league.is_not(TypeLeague.TOP_20_CLUB_LEAGUE)
    )
)
async def select_type_league_statistic_matches(
    query: CallbackQuery,
    callback_data: SelectTypeMatchLeague,
    character: Character
):
    group_ids = await LeagueService.get_group_ids_by_league(
        type_league=callback_data.type_league
    )
    if not group_ids:
        league_config = GetConfig.get_config(callback_data.type_league)

        date_state_league = league_config.DATETIME_START_LEAGUE.strftime("%d.%m.%Y")
        end_time_league = league_config.DATETIME_END_LEAGUE.strftime("%d.%m.%Y")

        text = (
            "<b>⚠️ Матчі цієї ліги ще не почалися!</b>\n\n"
            f"📅 Початок: <b>{date_state_league}</b>\n"
            f"🏁 Завершення: <b>{end_time_league}</b>\n\n"
            "Слідкуй за оновленнями, щоби не пропустити старт!"
        )

        return await query.message.answer(
            text=text,
        )
    my_group_id = None
    if character.club_id:
        my_group_id = await LeagueService.get_group_id_by_club_and_type_league(
            club_id=character.club_id,
            type_league=callback_data.type_league
        )
    await query.message.edit_text(
        text="Оберіть яку групу хочете дивитися",
        reply_markup=select_group(group_ids, my_group_id)
    )