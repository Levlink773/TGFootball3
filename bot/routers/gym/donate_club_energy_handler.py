from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models.character import Character
from database.models.league_fight import LeagueFight

from services.character_service import CharacterService
from services.club_service import ClubService

from bot.callbacks.gym_calbacks import SelectCountDonateEnergy
from bot.keyboards.gym_keyboard import select_donate_energy_keyboard, no_energy_keyboard
from bot.states.gym_state import SelectCountDonateEnergyState
from bot.filters.check_time_filter import CheckTimeFilterMessage

from utils.gym_utils import get_text_training_facilities

donate_club_energy_router = Router()


@donate_club_energy_router.message(F.text.regexp(r"^(✅\s*)?💪🏻 Посилення команди(\s*✅)?$"))
async def training_facilities_handler(message: Message, character: Character, state: FSMContext):

    if not character.club_id:
        return await message.answer("❌ Ви не перебуваєте в команді, тому ви не можете отримати від команди посилення")
    
    await message.answer("Вітаю на тренувальній базі\n<b>Покращення діє лише на наступний матч!</b>")
    
    await state.set_state(SelectCountDonateEnergyState.select_count_energy)
    club = await ClubService.get_club(club_id=character.club_id)
    await message.answer(text = get_text_training_facilities(club=club),
                         reply_markup=select_donate_energy_keyboard(
                             club_id=character.club_id
                         ))

@donate_club_energy_router.callback_query(
    SelectCountDonateEnergy.filter(),
    SelectCountDonateEnergyState.select_count_energy,
    CheckTimeFilterMessage()
)
async def select_count_donate_energy_callback_handler(
    query: CallbackQuery, 
    state: FSMContext,
    character: Character,
    callback_data: SelectCountDonateEnergy
):
    if not character.club_id == callback_data.club_id:
        return await query.answer("Ви вже не перебуваєте в той команді, щоб задонатити енергію")
        
    if callback_data.count_energy > character.current_energy:
        return await query.message.answer(
            text = "У вас не вистачає енергії, ви можете купити енергію в Крамниці енергії",
            reply_markup = no_energy_keyboard()
        ) 
    
    club = await ClubService.get_club(club_id=character.club_id)
    
    if club.energy_applied + callback_data.count_energy > 500:
        return await query.message.answer("Вашим поповненням ви перевищите ліміт максимального пожертвування команди\n"\
                                          "Ви можете поповнити на енергію на {max_energy_donate}".format(
                                              max_energy_donate = int(500 - club.energy_applied)
                                          ))
    

    
    await ClubService.donate_energy(club=club, count_energy=callback_data.count_energy)
    await CharacterService.consume_energy(character_id=character.id,
                                          energy_consumed=callback_data.count_energy)
    await query.message.answer(f"Вітаю ви поповнили енергію у свою команду на {callback_data.count_energy} 🔋")
    await state.clear()
    

@donate_club_energy_router.message((F.text.func(str.isdigit)),
                                    SelectCountDonateEnergyState.select_count_energy,
                                    CheckTimeFilterMessage())
async def select_count_donate_energy_message_handler(message: Message, state: FSMContext,
                                                     character: Character):
    count_energy = int(message.text)
    
    if count_energy > character.current_energy:
        return await message.answer(
            text = "У вас не вистачає енергії, ви можете купити енергію в Крамниці енергії",
            reply_markup = no_energy_keyboard()
        ) 
    club = await ClubService.get_club(club_id=character.club_id)
    
    if club.energy_applied + count_energy > 500:
        return await message.answer("Вашим поповненням ви перевищите ліміт максимального пожертвування команди\n"\
                                          "Ви можете поповнити на енергію на {max_energy_donate}".format(
                                              max_energy_donate = int(500 - club.energy_applied)))
        
    await ClubService.donate_energy(club=club, count_energy=count_energy)
    await CharacterService.consume_energy(character_id=character.id,
                                          energy_consumed=count_energy)
    await message.answer(f"Вітаю ви поповнили енергію у свою команду на {count_energy} 🔋")
    await state.clear()

