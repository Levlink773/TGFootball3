import asyncio

from typing import Optional

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, FSInputFile

from database.models.user_bot import UserBot, STATUS_USER_REGISTER

from services.user_service import UserService

from loader import bot
from logging_config import logger

from .constans import (
    TIME_SLEEP_REGISTER_MESSAGE,
    TIME_FORGOT_MESSAGE,
    COUNT_FORGOT_MESSAGE
)
from .config import PHOTO_STAGE_REGISTER_USER, TEXT_STAGE_REGISTER_USER
from .keyboard.register_user import create_character

class StartRegisterUser:
    _bot: Bot = bot

    def __init__(self, user: UserBot):
        self.user = user
        self._status = user.status_register
        
        asyncio.create_task(self._forgot_register())
                
    async def _edit_status(self, new_status: STATUS_USER_REGISTER):
        await UserService.edit_status_register(
            user_id=self.user.user_id,
            status=new_status
        )
        self._status = new_status
        
    async def start_register_user(self) -> None:        
        await self._edit_status(
            new_status=STATUS_USER_REGISTER.START_REGISTER
        )
        await self._send_message(
            text = TEXT_STAGE_REGISTER_USER[self._status],
            photo = PHOTO_STAGE_REGISTER_USER[self._status]
        )
        await asyncio.sleep(TIME_SLEEP_REGISTER_MESSAGE)
        
        await self._edit_status(
            new_status=STATUS_USER_REGISTER.CREATER_CHARACTER
        )
        await self._send_message(
            text = TEXT_STAGE_REGISTER_USER[self._status],
            photo = PHOTO_STAGE_REGISTER_USER[self._status],
            keyboard = create_character()
        )
        
        
    async def _forgot_register(self) -> None:
        for _ in range(COUNT_FORGOT_MESSAGE):
            await asyncio.sleep(TIME_FORGOT_MESSAGE)
            user_end_training = await self._user_end_register()
            if user_end_training:
                break
            
    async def _user_end_register(self) -> bool:
        new_obj_user: UserBot = await UserService.get_user(
            user_id=self.user.user_id
        )
        if new_obj_user.status_register == STATUS_USER_REGISTER.END_TRAINING:
            return True
        
        await self._send_message(
                text = TEXT_STAGE_REGISTER_USER[STATUS_USER_REGISTER.FORGOT_TRAINING],
                photo = PHOTO_STAGE_REGISTER_USER[STATUS_USER_REGISTER.FORGOT_TRAINING]
            )
        return False 
            
    async def _send_message(
        self,
        text: str,
        photo: FSInputFile,
        keyboard: Optional[InlineKeyboardMarkup] = None,
    ) -> None:
        try:
            await self._bot.send_photo(
                chat_id=self.user.user_id,
                photo=photo,
                caption=text,
                reply_markup=keyboard,
            )
        except Exception as E:
            logger.error(f"Error sending message: {E}")
            
            
