import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from bot.routers.register_user.config import (
    PHOTO_STAGE_REGISTER_USER,
    TEXT_STAGE_REGISTER_USER
)
from bot.routers.register_user.state.register_user_state import RegisterUserState
from bot.routers.register_user.callbacks.create_character_callbacks import (
    CreateCharacter
)
from bot.routers.register_user.routers.join_to_club import join_to_club

from const_character import CREATE_CHARACTER_CONST

from database.models.user_bot import UserBot, STATUS_USER_REGISTER
from database.models.character import Character

from services.user_service import UserService
from services.character_service import CharacterService
from services.reminder_character_service import RemniderCharacterService

from .select_gender import select_gender_handler

create_character_router = Router()

@create_character_router.message(
    F.text == "СТВОРИТИ ПЕРСОНАЖА"    
)
async def start_command_handler(
    message: Message, 
    state: FSMContext, 
    user: UserBot, 
):
    new_status = STATUS_USER_REGISTER.SEND_NAME_CHARACTER
    
    await UserService.edit_status_register(
        user_id=user.user_id,
        status=new_status
    )
    await message.answer_photo(
        caption = TEXT_STAGE_REGISTER_USER[new_status],
        photo = PHOTO_STAGE_REGISTER_USER[new_status],
    )
    
    await state.set_state(RegisterUserState.send_name)
    

@create_character_router.message(
    RegisterUserState.send_name
)
async def save_name_handler(
    message: Message, 
    state: FSMContext, 
    user: UserBot, 
):
    character = await CharacterService.get_character(
        character_user_id=user.user_id
    )
    if character:
        return await message.answer(
            text = "Ви вже маєте персонажа!"
        )

    await state.update_data(
        name_character=message.text
    )
    await state.set_state(RegisterUserState.select_gender)
    await message.answer(
        text = f"🔹 <b>Тренер:</b> Запам’ятай, <b>{message.text}</b>, твоє ім’я можуть скандувати тисячі фанатів, якщо покажеш, на що здатен!"
    )
    await asyncio.sleep(1)
    await select_gender_handler(
        message=message,
        user=user
    )
    
@create_character_router.callback_query(
    CreateCharacter.filter(),
    RegisterUserState.select_gender
)
async def create_character_handler(
    query: CallbackQuery,
    callback_data: CreateCharacter,
    state: FSMContext,
    user: UserBot,
):
    data = await state.get_data()
    name_character = data.get("name_character", None)
    if not name_character:
        return await start_command_handler(
            message=query.message,
            state=state,
            user=user
        )
    
    const_character = CREATE_CHARACTER_CONST(
        position = callback_data.position
    )
    character_obj = await CharacterService.get_character(
        character_user_id = user.user_id
    )
    if character_obj:
        await state.clear()
        await query.answer(
            text = "Ви вже маєте персонажа!",
        )
        await join_to_club(
            character=character_obj,
            message = query.message,
            state=state
        )
        return 

    character_obj = Character(
        current_energy = 150,
        characters_user_id = user.user_id,
        name = name_character,
        technique = const_character.technique,
        kicks = const_character.kicks,
        ball_selection = const_character.ball_selection,
        speed = const_character.speed,
        endurance = const_character.endurance,
        position = callback_data.position,
        gender = callback_data.gender,
        club_id = None,
        is_bot = False,
        referal_user_id = user.referal_user_id
        
    )
    
    await CharacterService.create_character(
        character_obj = character_obj 
    )
    new_character_user = await CharacterService.get_character(
        character_user_id = user.user_id
    )
    await RemniderCharacterService.create_character_reminder(character_id=new_character_user.id)
    await state.clear()
    await query.message.edit_caption(
        caption = f"""
🔹 <b>Тренер</b>: Чудовий вибір, <b>{name_character}</b>! Запам’ятай: твоя позиція – це не просто місце на полі, а твоя роль у команді!    
""",
    )
    await query.message.answer(
        text="""
<b>👨‍🏫 Тренер: Слухай уважно, новачок!"</b>
Перед тобою короткий вступ. Я покажу, як тут усе працює.
🎁 І так, за старанність отримаєш +300 сили після завершення!
        """
    )
    message_delete_keyboard =await query.bot.send_message(
        chat_id = query.message.chat.id,
        text = ".",
        reply_markup=ReplyKeyboardRemove()
    )
    await message_delete_keyboard.delete()
    await join_to_club(
        character=character_obj,
        message = query.message,
        state=state
    )

    