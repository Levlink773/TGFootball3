from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from bot.routers.register_user.config import (
    PHOTO_STAGE_REGISTER_USER,
    TEXT_STAGE_REGISTER_USER
)
from bot.routers.register_user.keyboard.select_position import (
    select_role_character,
    set_gender_keyboard,
)
from bot.routers.register_user.callbacks.create_character_callbacks import (
    SelectGender,
)

from database.models.user_bot import UserBot, STATUS_USER_REGISTER
from services.user_service import UserService

select_gender_router = Router()

async def select_gender_handler(
    user: UserBot,
    query: Optional[CallbackQuery] = None,
    message: Optional[Message] = None
):
    new_status = STATUS_USER_REGISTER.SELECT_GENDER
    await UserService.edit_status_register(
        user_id=user.user_id,
        status=new_status
    )
    if query:
        return await query.message.edit_media(
            media=InputMediaPhoto(
                media=PHOTO_STAGE_REGISTER_USER[new_status],
                caption=TEXT_STAGE_REGISTER_USER[new_status]
            ),
            reply_markup=set_gender_keyboard()
        )
        
    await message.answer_photo(
        caption = TEXT_STAGE_REGISTER_USER[new_status],
        photo = PHOTO_STAGE_REGISTER_USER[new_status],
        reply_markup = set_gender_keyboard()
    )

@select_gender_router.callback_query(
    F.data == "back_to_select_gender"
)
async def back_to_select_gender_handler(
    query: CallbackQuery,
    state: FSMContext,
    user: UserBot,
):
    await select_gender_handler(
        query=query,
        user=user
    )
    
@select_gender_router.callback_query(
    SelectGender.filter()
)
async def approved_position_handler(
    query: CallbackQuery,
    state: FSMContext,
    user: UserBot,
    callback_data: SelectGender
):
    await state.update_data(
        gender=callback_data.gender
    )
    new_status = STATUS_USER_REGISTER.SELECT_POSITION
    await UserService.edit_status_register(
        user_id=user.user_id,
        status=new_status
    )
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=PHOTO_STAGE_REGISTER_USER[new_status],
            caption=TEXT_STAGE_REGISTER_USER[new_status]
        ),
        reply_markup=select_role_character(callback_data.gender)
    )