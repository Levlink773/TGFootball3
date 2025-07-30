import time
import random

from aiogram import Router, F
from aiogram.types import  Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models.character import Character

from services.character_service import CharacterService

from bot.filters.donate_energy_filter import CheckTimeDonateEnergyMatch
from bot.callbacks.league_callbacks import EpizodeDonateEnergyToMatch
from bot.states.league_match_state import DonateEnergyInMatch
from bot.keyboards.gym_keyboard import no_energy_keyboard

from utils.photo_utils import get_photo, save_photo_id
from match.core.manager import ClubMatchManager
from match.entities import MatchData
from match.constans import (
    MIN_DONATE_ENERGY_TO_BONUS_KOEF,
    KOEF_DONATE_ENERGY,
    DONE_ENERGY_PHOTOS
)

from utils.club_utils import send_message_characters_club


add_energy_in_match_router = Router()

TEXT_EPIZODE_DONATE_ENERGY = """
⚡️ <b>Команда</b>: <u>{name_club}</u> зібрала <b>{min_donate_bonus_energy} енергії</b> в цьому епізоді!  
💪 Завдяки зусиллям гравців, команда отримує <b>BOOST</b> +{koef_add_power_from_donat}% до <b>суми донату</b>!

🔋 <b>Енергія — це сила!</b> Чим більше її Ви вкладаєте в епізод тим більший шанс збити гол!

👟 <b>Граємо далі</b> та йдемо до перемоги!
"""


@add_energy_in_match_router.callback_query(
    EpizodeDonateEnergyToMatch.filter(),
)
async def donate_energy_from_match_handler(
        query: CallbackQuery, 
        callback_data: EpizodeDonateEnergyToMatch, 
        character: Character,
        state: FSMContext
    ):

    if int(time.time()) > callback_data.time_end_goal:
        await query.answer("Час для цього голу вже закінчився",
                                  show_alert= True)
        return await query.message.delete()
    
    
    if character.club_id is None:
        await query.answer("Ви не перебуваєте в команді", 
                                  show_alert = True)
        return await query.message.delete()
    
    
    match_data = ClubMatchManager.get_match(callback_data.match_id)
    if not match_data:
        return
    
    if character.characters_user_id not in match_data.all_characters_user_ids_in_match:
        await query.answer("Ви не берете участь у цьому матчі", show_alert=True)
        return await query.message.delete()
    
    
    await state.update_data(match_data = match_data)
    await state.update_data(end_time = callback_data.time_end_goal)
    await state.set_state(DonateEnergyInMatch.send_epizode_donate_energy)
    await query.message.answer(f"Напишіть скільки ви хочете поповнити енергії в поточний матч\n1 енергія + 1 сила до команди в матчі\n\nПоточна енергія у тебе - {character.current_energy} 🔋")
    

@add_energy_in_match_router.message(
    DonateEnergyInMatch.send_epizode_donate_energy,
    (F.text.func(str.isdigit)),
    CheckTimeDonateEnergyMatch()
)
async def donate_epizode_energy(
    message: Message,
    character: Character,
    state: FSMContext
):
    
    MIN_ENERGY_DONATE_MATCH = 10
    energy = int(message.text)
    if energy < MIN_ENERGY_DONATE_MATCH:
        await state.clear()
        return await message.answer(f"Мінімум {MIN_ENERGY_DONATE_MATCH} енергії")
    
    if character.current_energy < energy:
        await state.clear()
        return await message.answer(
            text = "У вас не вистачає енергії, ви можете купити енергію в Крамниці енергії",
            reply_markup = no_energy_keyboard()
        ) 
        
    
    data = await state.get_data()
    end_time = data.get("end_time", None)
    match_data: MatchData = data.get("match_data", False)
    if not match_data or not end_time:
        await state.clear()
        return
    if int(time.time()) > end_time:
        await state.clear()
        return await message.answer(
            "Час для цього голу вже закінчився",
        )

    old_chance_club  = match_data.get_chance_clubs()
    old_first_club_chance = old_chance_club[0]*100
    old_second_club_chance = old_chance_club[1]*100
    
    if character.id in match_data.first_club.charactets_match_ids:
        match_data.first_club.epiіsode_donate_energy += energy
        my_club = match_data.first_club
        
    elif character.id in match_data.second_club.charactets_match_ids:
        match_data.second_club.epiіsode_donate_energy += energy
        my_club = match_data.second_club
    else:
        return
        
    if my_club.epiіsode_donate_energy >= MIN_DONATE_ENERGY_TO_BONUS_KOEF:
        if not my_club.text_is_send_epizode_donate_energy:
            random_patch = random.choice(DONE_ENERGY_PHOTOS)
            is_save, photo = await get_photo(random_patch)
            
            text_epizode_donate = TEXT_EPIZODE_DONATE_ENERGY.format(
                name_club = my_club.club_name,
                min_donate_bonus_energy = MIN_DONATE_ENERGY_TO_BONUS_KOEF,
                koef_add_power_from_donat = KOEF_DONATE_ENERGY*100
            )
            
            message_photo = await send_message_characters_club(
                characters_club = match_data.all_characters_in_clubs,
                my_character = None,
                text = text_epizode_donate,
                photo = photo,
            )
            my_club.text_is_send_epizode_donate_energy = True
            if message_photo and not is_save:
                await save_photo_id(
                    patch_to_photo = random_patch,
                    photo_id = message_photo.photo[0].file_id,
                )

                    
    after_chance_club = match_data.get_chance_clubs()
    chance_first_club_after = after_chance_club[0]*100
    chance_second_club_after = after_chance_club[1]*100
    
    text = f"""
⚽️ <b>{character.character_name} додав {energy}🔋 до сил команді {my_club.club_name}!</b> ⚽️  

🔥 <b>Зміни шансів на гол:</b>  
- ⚽️ Команда: {match_data.first_club.club_name} - <b>{old_first_club_chance:.2f}%</b> → <b>{chance_first_club_after:.2f}%</b>  
- ⚽️ Команда: {match_data.second_club.club_name} - <b>{old_second_club_chance:.2f}%</b> → <b>{chance_second_club_after:.2f}%</b>  

💪 Завдяки підтримці команда {my_club.club_name} отримала значний поштовх! 🚀 
    """
    await CharacterService.consume_energy(character_id=character.id, energy_consumed=energy)
    await send_message_characters_club(
        characters_club = match_data.all_characters_in_clubs,
        my_character = None,
        text = text
    )