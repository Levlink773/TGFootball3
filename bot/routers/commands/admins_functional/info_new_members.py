import asyncio

from aiogram import Router, F
from aiogram.types import Message, InputMediaDocument, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from bot.filters.check_admin_filter import CheckUserIsAdmin
from bot.states.admin_comands_state import GetInfoMember
from bot.utils.xls.generate_new_member import GenerateNewMemberXLS

from services.admins_functional_service import AdminFunctionalService

from logging_config import logger

admin_info_new_member_router = Router()

@admin_info_new_member_router.message(
    Command("info_new_member"), 
    CheckUserIsAdmin()
)
async def new_info_member_handler(
    message: Message,
    state: FSMContext,
):
    await message.answer(
        text = "Напишіть кількість нових гравців, про яких ви хочете дізнатися.",
    )
    await state.set_state(GetInfoMember.send_count_new_members)
    
@admin_info_new_member_router.message(
    GetInfoMember.send_count_new_members,
    CheckUserIsAdmin()
)
async def get_count_new_members_handler(
    message: Message,
    state: FSMContext
):
    try:
        count_new_member = int(message.text)
    except:
        await state.clear()
        await message.answer(
            text = "Ще раз натисніть /info_new_member, щоб почати спочатку.",
        )
        return
        
    new_characters = await AdminFunctionalService.get_new_members_character(
        count_members=count_new_member
    )
    message_start_generate = await message.answer(
        "Генерація звіту о нових гравцях...",
    )
    
    generator_xls = GenerateNewMemberXLS(
        members=new_characters
    )
    await generator_xls.generate_xls()
    xls_bytes = generator_xls.save_to_bytes()
    
    await message_start_generate.edit_media(
        media = InputMediaDocument(
            media = BufferedInputFile(
                xls_bytes, 
                filename=f"Звіт о нових гравцях[{count_new_member}].xlsx"),
            caption = "Звіт о нових гравцях",
        )
    )
    await state.clear()