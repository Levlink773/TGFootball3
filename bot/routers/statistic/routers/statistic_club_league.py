from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.routers.statistic.keyboard.menu_club_league_statistic import (
    menu_club_league_statistic,
    select_club_league_statistic
)
from bot.routers.statistic.callbacks.club_league_callbacks import (
    SelectClubLeagueStatistic,
    ViewClubLeagueStatistic
)
from bot.callbacks.switcher import SwitchLeagueClub

from utils.club_utils import get_club_description

from services.club_service import ClubService

menu_choice_league_club_router = Router()

@menu_choice_league_club_router.message(
    F.text == "📊 Команди в лігах"
)
async def menu_statistic_handler(
    message: Message,
):
    await message.answer(
        text = "Виберіть статистику, яку ви хочете переглянути.",
        reply_markup=menu_club_league_statistic()
    )
    

@menu_choice_league_club_router.callback_query(
    SelectClubLeagueStatistic.filter()
)
async def menu_club_league_statistic_handler(
    query: CallbackQuery,
    callback_data: SelectClubLeagueStatistic,
    state: FSMContext
):
    
    statistic_club_league = await ClubService.get_clubs_by_league(
        league = callback_data.league,
    )
    if not statistic_club_league:
        await query.answer(
            text = "У цій лізі немає клубів.",
            show_alert = True
        )
        return
    text = """
Ви вибрали статистику по лізі {league}
Виберіть клуб, статистику якого ви хочете переглянути.
    """
    await state.update_data(
        statistic_club_league = statistic_club_league
    )

    await query.message.answer(
        text = text.format(league=callback_data.league),
        reply_markup=select_club_league_statistic(
            league_clubs = statistic_club_league,
            page = 0
        )
    )
    
@menu_choice_league_club_router.callback_query(
    ViewClubLeagueStatistic.filter()
)
async def view_club_league_statistic_handler(
    query: CallbackQuery,
    callback_data: ViewClubLeagueStatistic,
):

    club = await ClubService.get_club(
        club_id = callback_data.club_id,
    )
    text = await get_club_description(club)
    await query.message.answer_photo(
        photo = club.custom_photo_stadion,
        caption = text
    )
    
    
@menu_choice_league_club_router.callback_query(
    SwitchLeagueClub.filter()
)
async def switch_league_club_handler(
    query: CallbackQuery,
    callback_data: SwitchLeagueClub,
    state: FSMContext
):
    data = await state.get_data()
    statistic_club_league = data.get("statistic_club_league", [])
    if not statistic_club_league:
        return await menu_statistic_handler(query.message)
        
    page = callback_data.page
    await query.message.edit_reply_markup(
        reply_markup=menu_club_league_statistic(
            league_clubs = statistic_club_league,
            page = page,
        )
    ) 