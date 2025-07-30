from aiogram import Router, F
from aiogram.types import Message

from database.models.character import Character

from services.character_service import CharacterService
from services.club_service import ClubService
from services.match_character_service import MatchCharacterService
from services.duel_service import DuelService

from services.league_services.default_league_service import DefaultLeagueService
from services.league_services.league_service import LeagueService
from services.league_services.top_20_club_league_service import Top20ClubLeagueService

from bot.keyboards.hall_fame_keyboard import menu_hall_fame

from utils.hall_fame_utils import (
    get_top_characters_by_power,
    get_top_characters_by_level,
    get_top_club_by_power,
    get_top_bomber_rating,
    get_top_duelists_ranking,
    get_top_24_clubs_text
)
from constants import HALL_FAME_PHOTO, DUEL_END_DAY_SEASON, DUEL_START_DAY_SEASON

from datetime import datetime

hall_fame_router = Router()


@hall_fame_router.message(
    F.text.regexp(r"(✅\s*)?🏆 Зал слави(\s*✅)?")
)
async def menu_hall_of_fame(message: Message):
    await message.answer_photo(
        photo=HALL_FAME_PHOTO,
        caption="Ви прийшли в зал слави",
        reply_markup=menu_hall_fame()
    )
    
@hall_fame_router.message(F.text == "💪Рейтинг за силою гравця")
async def menu_hall_of_fame(message: Message, character: Character):
    all_characters = await CharacterService.get_all_users_not_bot()
    await message.answer(
        text=get_top_characters_by_power(
            all_characters=all_characters,
            my_character=character
        )
    )
    

@hall_fame_router.message(F.text == "📊 Рейтинг за рівнем гравця")
async def menu_hall_of_fame(message: Message, character: Character):
    all_characters = await CharacterService.get_all_users_not_bot()
    await message.answer(
        text=get_top_characters_by_level(
            all_characters=all_characters,
            my_character=character
        )
    )
    
    

@hall_fame_router.message(F.text == "🏆 Рейтинг команд за силою")
async def menu_hall_of_fame(message: Message, character: Character):
    my_club = await ClubService.get_club(club_id=character.club_id)
    all_clubs = await ClubService.get_all_clubs()

    await message.answer(
        text=get_top_club_by_power(
            all_clubs=all_clubs,
            my_club=my_club
        )
    )
    
@hall_fame_router.message(F.text == "🏃🏼 Рейтинг бомбардирів")
async def menu_hall_of_fame(message: Message, character: Character):
    group_id_mathces = await LeagueService.get_group_id_by_club(club_id=character.club_id)
    all_matches_charaters = await MatchCharacterService.get_characters_by_group_id(group_id_mathces)
    await message.answer(
        text=await get_top_bomber_rating(
            all_matches=all_matches_charaters,
            my_character=character
        )
    )

@hall_fame_router.message(F.text == "👥 Рейтинг ПВП-пеналті")
async def menu_hall_of_fame(message: Message, character: Character):
    if not (datetime.now().day >= DUEL_START_DAY_SEASON) and not (datetime.now().day <= DUEL_END_DAY_SEASON):
        return message.answer("Еще нету дуелей")
    
    all_duels = await DuelService.get_season_duels()
    await message.answer(
        text = get_top_duelists_ranking(
            all_duels,
            my_character=character
        )
        
        
    )
    
@hall_fame_router.message(F.text == "📊 Клубний рейтинг")
async def menu_hall_of_fame_best_24_club(message: Message):
    await message.answer(
        text = await get_top_24_clubs_text()
    )
    