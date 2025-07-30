from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.league_services.league_service import LeagueService

from utils.league_utils import (
    get_text_rating
)

from ...callbacks.match_statistic_callbacks import StatisticsMatches

statistics_matches_router = Router()


@statistics_matches_router.callback_query(StatisticsMatches.filter())
async def select_group_handler(
    query: CallbackQuery,
    callback_data: StatisticsMatches,
):
    await send_statisitcs_matches(
        query=query,
        group_id=callback_data.group_id,
    )

async def send_statisitcs_matches(
    query: CallbackQuery,
    group_id: int,
):
    league_matches = await LeagueService.get_month_league_by_group(
        group_id=group_id
    )
    if not league_matches:
        return await query.message.answer(
            text="Немає матчів"
        )
        
    await query.message.answer(
        text=await get_text_rating(fights=league_matches)
    )