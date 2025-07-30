from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from bot.keyboards.club_keyboard import (
    select_option_custom_stadion, 
    menu_photo_custom_stadion,
    aproved_photo_stadion
    )
from bot.filters.check_admin_club_filter import CheckOwnerClub
from bot.states.club_states import SendCustomNameStadion
from bot.callbacks.club_callbacks import SelectPhotoStadion, ApprovedPhotoStadion

from database.models.character import Character
from database.models.club import Club

from services.club_service import ClubService

custom_stadion_router = Router()


@custom_stadion_router.callback_query(F.data == "custom_stadion", CheckOwnerClub())
async def menu_custom_stadion_handler(query: CallbackQuery):    
    await query.message.answer(
        "Виберіть опції для кастомного налаштування стадіону",
        reply_markup = select_option_custom_stadion()
    )
    
@custom_stadion_router.callback_query(F.data == "select_custom_stadion_name", CheckOwnerClub())
async def send_message_select_name_stadion_handler(query: CallbackQuery, state: FSMContext):
    await state.set_state(SendCustomNameStadion.send_name)
    await query.message.answer("Введи свою назву стадіону, яка відображатиметься в початковій лізі")

@custom_stadion_router.message(SendCustomNameStadion.send_name, CheckOwnerClub())
async def send_new_name_stadion_handler(message: Message, state: FSMContext, character: Character):
    new_name_stadion = message.text
    await ClubService.change_name_stadion(
        club_id = character.club_id,
        new_name_stadion = new_name_stadion
    )
    await message.answer(f"Ві поставили нову назву для стадіону: {new_name_stadion}")
    await state.clear()
    
@custom_stadion_router.callback_query(F.data == "select_custom_stadion_photo", CheckOwnerClub())
async def get_menu_photo_club_stadion_handler(query: CallbackQuery):
    await query.message.answer(
        "Виберіть фото для стадіону",
        reply_markup = menu_photo_custom_stadion()
    )

@custom_stadion_router.callback_query(SelectPhotoStadion.filter(), CheckOwnerClub())
async def select_photo(query: CallbackQuery, callback_data: SelectPhotoStadion):
    photo = FSInputFile(
        callback_data.patch_to_photo
    )
    await query.message.answer_photo(
        photo = photo,
        caption = "Вибрати це фото як фото для стадіону?",
        reply_markup = aproved_photo_stadion(
            patch_to_photo = callback_data.patch_to_photo
        )
    )
    
@custom_stadion_router.callback_query(ApprovedPhotoStadion.filter(), CheckOwnerClub())
async def aprove_photo_stadion_handler(query: CallbackQuery, callback_data: ApprovedPhotoStadion, character: Character):
    await ClubService.change_photo_url_stadion(
        club_id = character.club_id,
        photo_url = callback_data.patch_to_photo
    )
    await query.message.reply(
        text = "Ви вибрали для стадіону цю фотографію"
    )