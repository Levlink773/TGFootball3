import asyncio

from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from database.models.club import Club
from database.models.character import Character

from services.club_service import ClubService
from services.character_service import CharacterService

from bot.states.club_states import FindClub
from bot.keyboards.club_keyboard import find_club, join_to_club_keyboard, main_menu_club
from bot.callbacks.club_callbacks import SelectClubToJoin, JoinToClub
from bot.callbacks.switcher import SwitchClub

from constants import TIME_TO_JOIN_TO_CLUB

from logging_config import logger

from constants import CLUB_PHOTO
from utils.club_utils import get_club_description, send_message_characters_club
from .utils import send_message_approved_user

find_club_router = Router()

@find_club_router.message(F.text == "🎮 Приєднатися до команди")
async def get_my_club_handler(message: Message, state: FSMContext, character: Character):
    if character.club_id:
        return await message.answer("Ви вже й так у команді")
    
    all_clubs = await ClubService.get_all_clubs_to_join()
    await state.update_data(all_clubs = all_clubs)
    if not all_clubs:
        return await message.reply("На даний момент немає команд")
        
    await state.set_state(FindClub.send_name_club)
    await message.answer("Виберіть команду зі списку, або введіть назву команди самостійно",
                               reply_markup=find_club(
                                   all_clubs=all_clubs,
                                   page=0
                               ))
    
    
@find_club_router.message(FindClub.send_name_club, F.text != "⛩ Створити свою команду")
async def find_clube_message(message: Message, state: FSMContext, character: Character):
    if  character.club_id:
        return await message.answer("Ви вже й так у команді")
    data = await state.get_data()
    all_clubs: list[Club] = data['all_clubs']
    matching_clubs = [club for club in all_clubs if message.text.lower() in club.name_club.lower()]
    await state.update_data(all_clubs = matching_clubs)
    if not matching_clubs:
        return await message.answer(f"Команд за назвою - {message.text}, не знайдено")
    
    await message.answer(
        f"Усі знайдені команди за назвою - {message.text}",
        reply_markup=find_club(
            all_clubs=matching_clubs,
            page=0
        )
    )
    
@find_club_router.callback_query(SwitchClub.filter())
async def switcher_select_club(query: CallbackQuery, callback_data: SwitchClub, state: FSMContext):
    data = await state.get_data()
    if not data.get("all_clubs", False):
        return
    return await query.message.edit_reply_markup(
        reply_markup= find_club(
            all_clubs=data['all_clubs'],
            page=callback_data.page
        )
    )


@find_club_router.callback_query(SelectClubToJoin.filter())
async def view_club(query: CallbackQuery, callback_data: SelectClubToJoin):
    club = await ClubService.get_club(club_id=callback_data.club_id)
    await query.message.answer_photo(
        photo=CLUB_PHOTO,
        caption=await get_club_description(club=club),
        reply_markup=join_to_club_keyboard(club_id=callback_data.club_id)
    )
    
@find_club_router.callback_query(JoinToClub.filter())
async def join_to_club(query: CallbackQuery, state: FSMContext, callback_data: JoinToClub, character: Character):
    club = await ClubService.get_club(callback_data.club_id)
    
    if not club:
        return await query.answer("Команда не знайдена", show_alert=True)
    
    if club.is_invite_only:
        await query.answer("Ви надіслали запрошення до клубу, очікуйте результатів", show_alert=True)
        return await send_message_approved_user(
            user_how_join=character,
            club=club
        )
    
    await asyncio.sleep(0.5)
    if len(club.characters) >= 11:
        return await query.message.answer("Перевищено ліміт людей у клубі")
    
    if character.reminder.time_to_join_club  + TIME_TO_JOIN_TO_CLUB > datetime.now():
        remaining_time = (character.reminder.time_to_join_club + TIME_TO_JOIN_TO_CLUB) - datetime.now()
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return await query.answer(
            f"Ви не можете приєднатися до команди, залишилось {hours} годин та {minutes} хвилин до моменту, коли можна приєднатися.",
            show_alert=True
        )
    
    if character.club_id:
        return await query.message.answer("Ви вже й так у команді")
    
    await state.clear()
    await CharacterService.update_character_club_id(
        character=character,
        club_id=callback_data.club_id
    )

    await send_message_characters_club(
        characters_club=club.characters,
        my_character=character,
        text=f"🎟 Вітаємо у вашій команді поповнення, приєднався новий учасник <b>{character.character_name}</b>"
    )
    character = await CharacterService.get_character_by_id(character.id)
    await query.message.answer("🎉 Вітаю ви приєдналися до команди", 
                               reply_markup=main_menu_club(character))
    
