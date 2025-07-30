from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models.character import Character

from services.club_service import ClubService

from bot.keyboards.club_keyboard import view_club, view_character_club
from bot.callbacks.club_callbacks import SelectClubToView

from utils.club_utils import get_club_description

research_club_router = Router()

@research_club_router.message(F.text == "🧿 Переглянути інші команди")
async def research_club_handler(message: Message, character: Character, state: FSMContext):    
    all_clubs = await ClubService.get_all_clubs_to_join()
    all_clubs_not_my_club = [club for club in all_clubs if club.id != character.club_id if not club.is_fake_club]
    await state.update_data(all_clubs = all_clubs_not_my_club)
    if not all_clubs_not_my_club:
        return await message.answer("Немає команд для перегляду")
    
    await state.update_data(all_clubs_not_my_club = all_clubs_not_my_club)
        
    await message.answer("Виберіть команду зі списку, або введіть назву команди самостійно",
                               reply_markup=view_club(
                                   all_clubs=all_clubs_not_my_club,
                                   page = 0
                               )) 
    
@research_club_router.callback_query(SelectClubToView.filter())
async def view_other_club_handler(
    query: CallbackQuery, 
    callback_data: SelectClubToView
):    
    club = await ClubService.get_club(club_id= callback_data.club_id)
    await query.message.answer(
        text=await get_club_description(club),
        reply_markup=view_character_club(club.id)
    )