from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.league_keyboard import menu_national_cup_ukraine, keyboard_to_join_character_to_fight
from bot.filters.user_in_club_filter import UserInClub, ClubIn20PowerLeague


from database.models.character import Character

# from services.best_20_club_league_service import Best20ClubLeagueService
from services.club_service import ClubService
from services.league_services.league_service import LeagueService
from services.league_services.top_20_club_league_service import Top20ClubLeagueService


from constants import LEAGUE_PHOTO, JOIN_TO_FIGHT
from constants import TIME_FIGHT

from utils.league_utils import get_text_top_club_text, get_text_calendar_matches, get_text_result, get_text_rating


best_20_club_league_router = Router()


@best_20_club_league_router.message(F.text == "🏆 Національний Кубок України", UserInClub(), ClubIn20PowerLeague())
async def menu_best_league(message: Message, character: Character):
    club = await ClubService.get_club(club_id=character.club_id)
    await message.answer_photo(
        photo=LEAGUE_PHOTO,
        caption=await get_text_top_club_text(club),
        reply_markup=menu_national_cup_ukraine()
    )    

@best_20_club_league_router.message(F.text == "📝 Зареєструватися в матч Кубка України", UserInClub(), ClubIn20PowerLeague())
async def register_character_to_match(message: Message, character: Character):
    club = await ClubService.get_club(club_id=character.club_id)
    next_match = await Top20ClubLeagueService.get_next_league_fight_by_club(
        club_id=character.club_id
    )
    if not next_match:
        return await message.answer("На даний момент немає матчів")
    await message.answer_photo(
        photo=JOIN_TO_FIGHT,
        caption=await get_text_top_club_text(club),
        reply_markup=keyboard_to_join_character_to_fight(
            match_id=next_match.match_id
        )
    )

# @best_20_club_league_router.message(F.text == "🔋 Задонатити в матч Кубка України", UserInClub(), ClubIn20PowerLeague())
# async def donate_energy_to_match(message: Message, character: Character, state: FSMContext):
#     if character.club_id is None:
#         return await message.answer("Ви не перебуваєте в команді")
    

#     current_match_db = await Best20ClubLeagueService.get_next_top_20_league_fight_by_club(
#         club_id=character.club_id
#     )

#     if current_match_db is None:
#         return await message.answer("На даний момент немає матчів")
    
#     current_match = ClubMatchManager.get_fight_by_id(current_match_db.match_id)
#     await state.update_data(current_match = current_match)
    
#     current_datetime = datetime.now()
#     if (current_datetime < current_match.start_time) or (current_datetime > current_match.start_time + TIME_FIGHT):
#         return await message.answer("Зараз не час поповнювати енергію, можна буде поповнити її протягом матчу")
    
#     await state.set_state(DonateEnergyInMatch.send_count_donate_energy)
#     await message.answer(f"Напишіть скільки ви хочете поповнити енергії в поточний матч\n5 енергії + 1 сила до команди в матчі\n\nПоточна енергія у тебе - {character.current_energy} 🔋")
    

@best_20_club_league_router.message(F.text == "📅 Календар Кубка України", UserInClub(), ClubIn20PowerLeague())
async def get_calendar_matches(message: Message, character: Character):
    all_matches = await Top20ClubLeagueService.get_month_league_by_club(club_id=character.club_id)
    await message.answer(
        text=get_text_calendar_matches(matches=all_matches, club_id=character.club_id)
    )
    
@best_20_club_league_router.message(F.text == "📊 Результати Кубка України", UserInClub(), ClubIn20PowerLeague())
async def get_result_matches(message: Message, character: Character):    
    all_matches = await Top20ClubLeagueService.get_month_league_by_club(club_id=character.club_id)
    await message.answer(
        text=get_text_result(fights=all_matches, club_id=character.club_id)
    )
    
@best_20_club_league_router.message(F.text == "📋 Таблиця Кубка України", UserInClub(), ClubIn20PowerLeague())
async def get_table_rait(message: Message, character: Character):
    next_match = await Top20ClubLeagueService.get_next_league_fight_by_club(
        club_id=character.club_id
    )
    all_mathes_by_group = await LeagueService.get_month_league_by_group(group_id=next_match.group_id)
    await message.answer(
        text=await get_text_rating(all_mathes_by_group)
    )