from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models.user_bot import UserBot
from database.models.character import Character

from bot.keyboards.character_keyboard import character_keyboard


from constants import get_photo_character
from utils.character_utils import get_character_text, get_referal_text



menu_character_router = Router()

@menu_character_router.message(
    F.text.regexp(r"(✅\s*)?🏃‍♂️ Мій футболіст(\s*✅)?")
)
async def get_my_character(message: Message, state: FSMContext, character: Character):

    await state.clear()
    await message.answer_photo(
        photo=get_photo_character(character),
        caption=get_character_text(character),
        reply_markup=character_keyboard()
    )
    

    
@menu_character_router.callback_query(F.data == "referal_system")
async def character_referal_handler(query: CallbackQuery, character: Character):
    await query.message.answer(
        text = await get_referal_text(my_character=character)
    )