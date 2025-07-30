
from aiogram import Router, F
from aiogram.types import Message

from bot.keyboards.league_keyboard import menu_new_club_league, keyboard_to_join_character_to_fight
from bot.filters.user_in_club_filter import UserInClub, ClubInNewClubLeague


from database.models.character import Character

from services.club_service import ClubService
from services.league_services.league_service import LeagueService
from services.league_services.new_clubs_league_service import NewClubsLeagueService


from constants import LEAGUE_PHOTO, JOIN_TO_FIGHT
from constants import TIME_FIGHT

from utils.league_utils import (
    get_text_new_club_league, 
    get_text_calendar_matches, 
    get_text_result, 
    get_text_rating
)


new_club_league_router = Router()


@new_club_league_router.message(
    F.text == "🏆 Ліга нових клубів", 
    UserInClub(), 
    ClubInNewClubLeague()
)
async def new_club_league_handler(message: Message, character: Character):
    club = await ClubService.get_club(club_id=character.club_id)
    await message.answer_photo(
        photo=LEAGUE_PHOTO,
        caption=await get_text_new_club_league(club),
        reply_markup=menu_new_club_league()
    )    

@new_club_league_router.message(
    F.text == "📝 Зареєструватися в матч Нових клубів", 
    UserInClub(), 
    ClubInNewClubLeague()
)
async def register_character_to_match(message: Message, character: Character):
    club = await ClubService.get_club(club_id=character.club_id)
    next_match = await NewClubsLeagueService.get_next_league_fight_by_club(
        club_id=character.club_id
    )
    if not next_match:
        return await message.answer("На даний момент немає матчів")
    await message.answer_photo(
        photo=JOIN_TO_FIGHT,
        caption=await get_text_new_club_league(club),
        reply_markup=keyboard_to_join_character_to_fight(
            match_id=next_match.match_id
        )
    )


@new_club_league_router.message(
    F.text == "📅 Календар Нових клубів", 
    UserInClub(), 
    ClubInNewClubLeague()
)
async def get_calendar_matches(message: Message, character: Character):
    all_matches = await NewClubsLeagueService.get_month_league_by_club(club_id=character.club_id)
    await message.answer(
        text=get_text_calendar_matches(matches=all_matches, club_id=character.club_id)
    )
    
@new_club_league_router.message(
    F.text == "📊 Результати Нових клубів", 
    UserInClub(), 
    ClubInNewClubLeague()
)
async def get_result_matches(message: Message, character: Character):    
    all_matches = await NewClubsLeagueService.get_month_league_by_club(club_id=character.club_id)
    await message.answer(
        text=get_text_result(fights=all_matches, club_id=character.club_id)
    )
    
@new_club_league_router.message(
    F.text == "📋 Таблиця Нових клубів", 
    UserInClub(), 
    ClubInNewClubLeague()
)
async def get_table_rait(message: Message, character: Character):
    next_match = await NewClubsLeagueService.get_next_league_fight_by_club(
        club_id=character.club_id
    )
    all_mathes_by_group = await LeagueService.get_month_league_by_group(group_id=next_match.group_id)
    await message.answer(
        text=await get_text_rating(all_mathes_by_group)
    )