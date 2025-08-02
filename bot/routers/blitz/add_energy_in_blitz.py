import random
import time

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from blitz.blitz_match.core.manager import TeamBlitzMatchManager
from blitz.blitz_match.entities import BlitzMatchData
from bot.callbacks.blitz_callback import EpizodeDonateEnergyToBlitzMatch
from bot.filters.donate_energy_filter import CheckTimeDonateEnergyMatch
from bot.keyboards.gym_keyboard import no_energy_keyboard
from database.models.character import Character
from blitz.blitz_match.constans import (
    MIN_DONATE_ENERGY_TO_BONUS_KOEF,
    KOEF_DONATE_ENERGY,
    DONE_ENERGY_PHOTOS
)
from services.character_service import CharacterService
from utils.club_utils import send_message_characters_club
from utils.photo_utils import get_photo, save_photo_id

add_energy_in_match_router = Router()

TEXT_EPIZODE_DONATE_ENERGY = """
⚡️ <b>Команда</b>: <u>{name_team}</u> зібрала <b>{min_donate_bonus_energy} енергії</b> в цьому епізоді!  
💪 Завдяки зусиллям гравців, команда отримує <b>BOOST</b> +{koef_add_power_from_donat}% до <b>суми донату</b>!

🔋 <b>Енергія — це сила!</b> Чим більше її Ви вкладаєте в епізод тим більший шанс збити гол!

👟 <b>Граємо далі</b> та йдемо до перемоги!
"""


class DonateEnergyInBlitzMatch(StatesGroup):
    send_count_donate_energy = State()
    send_epizode_donate_energy = State()


@add_energy_in_match_router.callback_query(
    EpizodeDonateEnergyToBlitzMatch.filter(),
)
async def donate_energy_from_blitz_match_handler(
        query: CallbackQuery,
        callback_data: EpizodeDonateEnergyToBlitzMatch,
        character: Character,
        state: FSMContext
):
    if int(time.time()) > callback_data.time_end_goal:
        await query.answer("Час для цього голу вже закінчився",
                           show_alert=True)
        return await query.message.delete()

    match_data: BlitzMatchData = TeamBlitzMatchManager.get_match(callback_data.blitz_match_id)
    if not match_data:
        return

    if character.characters_user_id not in match_data.all_characters_user_ids_in_match:
        await query.answer("Ви не берете участь у цьому матчі", show_alert=True)
        return await query.message.delete()

    await state.update_data(match_data=match_data)
    await state.update_data(end_time=callback_data.time_end_goal)
    await state.set_state(DonateEnergyInBlitzMatch.send_epizode_donate_energy)
    await query.message.answer(
        f"Напишіть скільки ви хочете поповнити енергії в поточний матч\n1 енергія + 1 сила до команди в матчі\n\nПоточна енергія у тебе - {character.current_energy} 🔋")


@add_energy_in_match_router.message(
    DonateEnergyInBlitzMatch.send_epizode_donate_energy,
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
            text="У вас не вистачає енергії, ви можете купити енергію в Крамниці енергії",
            reply_markup=no_energy_keyboard()
        )

    data = await state.get_data()
    end_time = data.get("end_time", None)
    match_data: BlitzMatchData = data.get("match_data", False)
    if not match_data or not end_time:
        await state.clear()
        return
    if int(time.time()) > end_time:
        await state.clear()
        return await message.answer(
            "Час для цього голу вже закінчився",
        )

    old_chance_team = match_data.get_chance_teams()
    old_first_club_chance = old_chance_team[0] * 100
    old_second_club_chance = old_chance_team[1] * 100

    if character.id in match_data.first_team.charactets_match_ids:
        match_data.first_team.epiіsode_donate_energy += energy
        my_team = match_data.first_team

    elif character.id in match_data.second_team.charactets_match_ids:
        match_data.second_team.epiіsode_donate_energy += energy
        my_team = match_data.second_team
    else:
        return

    if my_team.epiіsode_donate_energy >= MIN_DONATE_ENERGY_TO_BONUS_KOEF:
        if not my_team.text_is_send_epizode_donate_energy:
            random_patch = random.choice(DONE_ENERGY_PHOTOS)
            is_save, photo = await get_photo(random_patch)

            text_epizode_donate = TEXT_EPIZODE_DONATE_ENERGY.format(
                name_team=my_team.team_name,
                min_donate_bonus_energy=MIN_DONATE_ENERGY_TO_BONUS_KOEF,
                koef_add_power_from_donat=KOEF_DONATE_ENERGY * 100
            )

            message_photo = await send_message_characters_club(
                characters_club=await match_data.all_characters_in_teams(),
                my_character=None,
                text=text_epizode_donate,
                photo=photo,
            )
            my_team.text_is_send_epizode_donate_energy = True
            if message_photo and not is_save:
                await save_photo_id(
                    patch_to_photo=random_patch,
                    photo_id=message_photo.photo[0].file_id,
                )

    after_chance_club = match_data.get_chance_teams()
    chance_first_team_after = after_chance_club[0] * 100
    chance_second_team_after = after_chance_club[1] * 100

    text = f"""
⚽️ <b>{character.character_name} додав {energy}🔋 до сил команді {my_team.team_name}!</b> ⚽️  

🔥 <b>Зміни шансів на гол:</b>  
- ⚽️ Команда: {match_data.first_team.team_name} - <b>{old_first_club_chance:.2f}%</b> → <b>{chance_first_team_after:.2f}%</b>  
- ⚽️ Команда: {match_data.second_team.team_name} - <b>{old_second_club_chance:.2f}%</b> → <b>{chance_second_team_after:.2f}%</b>  

💪 Завдяки підтримці команда {my_team.team_name} отримала значний поштовх! 🚀 
    """
    await CharacterService.consume_energy(character_id=character.id, energy_consumed=energy)
    await send_message_characters_club(
        characters_club=(await match_data.all_characters_in_teams()),
        my_character=None,
        text=text
    )
