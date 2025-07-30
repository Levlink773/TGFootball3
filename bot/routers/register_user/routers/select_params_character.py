from aiogram import Router, F
from aiogram.types import  CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.fsm.context import FSMContext

from bot.routers.register_user.config import (
    PHOTO_STAGE_REGISTER_USER,
    TEXT_STAGE_REGISTER_USER
)
from bot.routers.register_user.keyboard.select_position import (
    select_role_character,
    create_character
)
from bot.routers.register_user.callbacks.create_character_callbacks import (
    SelectPositionCharacter,
)
from bot.routers.register_user.config import TEXT_CHARACTER

from const_character import CREATE_CHARACTER_CONST
from constants import photos, Gender

from database.models.user_bot import UserBot, STATUS_USER_REGISTER

from services.user_service import UserService
from .select_gender import select_gender_handler

select_params_create_character_router = Router()

    
@select_params_create_character_router.callback_query(
    SelectPositionCharacter.filter()
)
async def select_position_handler(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: SelectPositionCharacter
):
    data = await state.get_data()
    gender: Gender = data.get("gender", None)
    name_character = data.get("name_character", None)
    if not gender or not name_character:
        return await query.answer(
            text="Створіть персонажа спочатку",
            show_alert=True
        )
        
    position = callback_data.position
    
    await state.update_data(
        position=callback_data.position
    )
    photo = FSInputFile(photos[(gender, position)])
    character = CREATE_CHARACTER_CONST(position)
    character.gender = gender
    text_character = TEXT_CHARACTER.format(
        character_name = name_character,
        gender = gender.value,
        effective_technique = character.effective_technique,
        effective_kicks = character.effective_kicks,
        effective_ball_selection = character.effective_ball_selection,
        effective_speed = character.effective_speed,
        effective_endurance = character.effective_endurance,
        full_power = character.full_power
    )
    await query.message.edit_media(
        media = InputMediaPhoto(
            media = photo,
            caption = text_character
        ),
        reply_markup = create_character(character),
    )
    
@select_params_create_character_router.callback_query(
    F.data == "select_other_position"
)
async def select_other_position_handler(
    query: CallbackQuery,
    state: FSMContext,
    user: UserBot,
):
    data = await state.get_data()
    gender = data.get("gender", None)
    if not gender:
        return await select_gender_handler(
            query=query,
            state=state,
            user=user
        )
        
    new_status = STATUS_USER_REGISTER.SELECT_POSITION
    await UserService.edit_status_register(
        user_id=user.user_id,
        status=new_status
    )
    await query.message.edit_media(
        media = InputMediaPhoto(
            media = PHOTO_STAGE_REGISTER_USER[new_status],
            caption = TEXT_STAGE_REGISTER_USER[new_status]
        ),
        reply_markup = select_role_character(gender)
    )
    
