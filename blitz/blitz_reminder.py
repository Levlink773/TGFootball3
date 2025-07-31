import asyncio
import traceback
from datetime import time, datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from blitz.blitz_register_service import BlitzRegisterService
from database.models.character import Character
from loader import bot
from services.character_service import CharacterService


async def _send_message(character: Character, text: str, reply_markup: InlineKeyboardMarkup = None):
    try:
        if character.is_bot:
            return

        await bot.send_message(
            chat_id=character.characters_user_id,
            text=text,
            reply_markup=reply_markup
        )
    except Exception as E:
        traceback.print_exc()
        print(E)


class BlitzReminder:
    def __init__(self,
                 start_time_blitz: time,
                 remind_for_simple_users: int = 30,
                 remind_for_vip_users: int = 20
                 ):
        self.start_time_blitz = start_time_blitz
        self.remind_for_simple_users = remind_for_simple_users
        self.remind_for_vip_users = remind_for_vip_users

    async def __reminder_blitz_for_users(self, characters: list[Character], required_vip: bool):
        filtered_characters = [
            character for character in characters
            if character.vip_pass_is_active == required_vip
        ]
        if not filtered_characters:
            return
        for character in filtered_characters:
            await _send_message(character, ("🔔 «Сьогодні о 15:00 блиц-турнір! Встигни зареєструватися та перемогти!»"
            if required_vip else "🔔 «До старту блиц-турніру залишилось 20 хвилин. Запис відкритий!»"),
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=
                                    [[InlineKeyboardButton(text="Зараєструватися", callback_data="")]]
                                ))

    async def remind(self):
        now = datetime.now()
        today_start = datetime.combine(now.date(), self.start_time_blitz)

        vip_remind_time = today_start - timedelta(minutes=self.remind_for_vip_users)
        simple_remind_time = today_start - timedelta(minutes=self.remind_for_simple_users)
        characters = await CharacterService.get_all_characters_where_end_training()
        if now < self.__start_time_as_datetime():
            if now < vip_remind_time:
                await asyncio.sleep((vip_remind_time - now).total_seconds())
                BlitzRegisterService.can_register = True
                await self.__reminder_blitz_for_users(characters, True)
            elif now < today_start:
                BlitzRegisterService.can_register = True
                await self.__reminder_blitz_for_users(characters, True)

        now = datetime.now()
        if now < self.__start_time_as_datetime():
            if now < simple_remind_time:
                await asyncio.sleep((simple_remind_time - now).total_seconds())
                await self.__reminder_blitz_for_users(characters, False)
            elif now < today_start:
                await self.__reminder_blitz_for_users(characters, False)
        # Ожидание до начала турнира (если нужно)
        now = datetime.now()
        if now < today_start:
            await asyncio.sleep((today_start - now).total_seconds())
        characters = await BlitzRegisterService.get_characters_from_blitz_character()
        for character in characters:
            await _send_message(character, "🚀 «Турнір почався! Граємо 1/8 фіналу!»")


    def __start_time_as_datetime(self) -> datetime:
        now = datetime.now()
        return datetime.combine(now.date(), self.start_time_blitz)
