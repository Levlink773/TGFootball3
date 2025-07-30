from aiogram import Router, F
from aiogram.types import Message

from bot.keyboards.league_keyboard import menu_beast_league_zone, keyboard_to_join_character_to_fight
from bot.filters.user_in_club_filter import UserInClub, ClubInBeastLeague

from database.models.character import Character

from constants import LEAGUE_PHOTO, JOIN_TO_FIGHT

from services.club_service import ClubService
from services.league_services.best_league_service import BestLeagueService 
from services.league_services.league_service import LeagueService


from utils.league_utils import get_text_league_devision, get_text_calendar_matches, get_text_result, get_text_rating


best_league_router = Router()


@best_league_router.message(F.text == "🏆 Єврокубки", UserInClub(), ClubInBeastLeague())
async def menu_best_league(message: Message, character: Character):
    club = await ClubService.get_club(club_id=character.club_id)
    await message.answer_photo(
        photo=LEAGUE_PHOTO,
        caption=await get_text_league_devision(club),
        reply_markup=menu_beast_league_zone()
    )    

@best_league_router.message(F.text == "📝 Зареєструватися в матч Єврокубків", UserInClub(), ClubInBeastLeague())
async def register_character_to_match(message: Message, character: Character):
    club = await ClubService.get_club(club_id=character.club_id)
    next_match = await BestLeagueService.get_next_league_fight_by_club(
        club_id=character.club_id
    )
    await message.answer_photo(
        photo=JOIN_TO_FIGHT,
        caption=await get_text_league_devision(club),
        reply_markup=keyboard_to_join_character_to_fight(
            match_id=next_match.match_id
        )
    )


@best_league_router.message(F.text == "📅 Календар Єврокубків", UserInClub(), ClubInBeastLeague())
async def get_calendar_matches(message: Message, character: Character):
    all_matches = await BestLeagueService.get_month_league_by_club(club_id=character.club_id)
    await message.answer(
        text=get_text_calendar_matches(matches=all_matches, club_id=character.club_id)
    )
    
@best_league_router.message(F.text == "📊 Результати Єврокубків", UserInClub(), ClubInBeastLeague())
async def get_result_matches(message: Message, character: Character):    
    all_matches = await BestLeagueService.get_month_league_by_club(club_id=character.club_id)
    await message.answer(
        text=get_text_result(fights=all_matches, club_id=character.club_id)
    )
    
@best_league_router.message(F.text == "📋 Таблиця Єврокубків", UserInClub(), ClubInBeastLeague())
async def get_table_rait(message: Message, character: Character):
    next_match = await BestLeagueService.get_next_league_fight_by_club(
        club_id=character.club_id
    )
    all_mathes_by_group = await LeagueService.get_month_league_by_group(group_id=next_match.group_id)
    await message.answer(
        text=await get_text_rating(all_mathes_by_group)
    )