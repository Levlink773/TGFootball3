import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from database.models.character import Character

from bot.filters.check_admin_filter import CheckUserIsAdmin
from bot.states.admin_comands_state import OptionsNewsletter
from bot.keyboards.admins_keyboard import select_option_newsletter

from services.character_service import CharacterService
from services.admins_functional_service import AdminFunctionalService

from utils.rate_limitter import rate_limiter

from logging_config import logger

admin_newsletter_commands = Router()

# @admin_newsletter_commands.message(Command("/test"))
# async def send_message(massage: Message):
#     for _ in range(500):
#         await send_message_to_character(
#             message = massage,
#             user_id = 6790393255
#         )

@admin_newsletter_commands.message(Command("send_message"), CheckUserIsAdmin())
async def send_message_all_user(message: Message, state: FSMContext):
    await message.answer("Выберите тип рассылки", 
                         reply_markup = select_option_newsletter())
    

@admin_newsletter_commands.callback_query(F.data == "newsletter_exp", CheckUserIsAdmin())
async def send_range_exp_newssletter(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Введите дипазон exp у персонажей\n\n10-300 - будет рассылка по пользователям, у которых от 10-300 exp")
    await state.set_state(OptionsNewsletter.send_range_exp)
    
@admin_newsletter_commands.message(OptionsNewsletter.send_range_exp, CheckUserIsAdmin())
async def send_exp_range(message: Message, state: FSMContext):
    try:
        min_exp, max_exp = (int(value) for value in message.text.split("-"))
        
        if min_exp > max_exp:
            return await message.answer("Минимальное кол-во експы, недолжно быть больше максимального")
        
        characters = await AdminFunctionalService.get_characters_by_exp(
            min_exp = min_exp,
            max_exp = max_exp
        )
        await state.update_data(characters = characters)
        await message.answer("Напишіть що завгодно, це повідомлення буде надіслано всім")
        await state.set_state(OptionsNewsletter.get_text_from_send)

    except ValueError as E:
        return await message.answer("Введите корректные данные")


@admin_newsletter_commands.callback_query(F.data == "newsletter_all_users", CheckUserIsAdmin())
async def send_message_all_character(query: CallbackQuery, state: FSMContext):
    characters = await CharacterService.get_all_users_not_bot()
    await state.update_data(characters = characters)
    await query.message.answer("Напишіть що завгодно, це повідомлення буде надіслано всім")
    await state.set_state(OptionsNewsletter.get_text_from_send)


    
@admin_newsletter_commands.message(OptionsNewsletter.get_text_from_send, CheckUserIsAdmin())
async def send_message(message: Message, state: FSMContext):
    data = await state.get_data()
    characterts: list[Character] = data.get("characters", False)
    if not characterts:
        return await message.answer("По новой выбери тип рассылки и т.д.")
     
    for user_character in characterts:
        try:
            await send_message_to_character(
                message = message,
                user_id = user_character.characters_user_id 
            )
        except Exception as E:
            logger.error(f"НЕ СМОГ ОТПРАВИТЬ ПРИ ТОТАЛЬНОЙ РАССЫЛКЕ - {user_character.name}")
    
    await message.answer("Розсилання цього повідомлення було закінчено")
    await state.clear()
    
@rate_limiter
async def send_message_to_character(message: Message, user_id: int) -> None:
    await message.send_copy(
        chat_id = user_id
    )
        