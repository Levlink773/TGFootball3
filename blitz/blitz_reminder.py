import asyncio
import traceback
from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from blitz.blitz_register_service import BlitzRegisterService
from bot.callbacks.blitz_callback import BlitzRegisterCallback
from database.models.blitz import Blitz
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
                 blitz: Blitz,
                 remind_for_simple_users: int = 20,
                 remind_for_vip_users: int = 30
                 ):
        self.blitz_start_at = blitz.start_at
        self.blitz_id = blitz.id
        self.remind_for_simple_users = remind_for_simple_users
        self.remind_for_vip_users = remind_for_vip_users

    async def __reminder_blitz_for_users(self, characters: list[Character], required_vip: bool, blitz_id: int):
        filtered_characters = [
            character for character in characters
            if character.vip_pass_is_active == required_vip
        ]
        if not filtered_characters:
            return
        text = ("🔔 «Сьогодні о 15:00 блиц-турнір! Встигни зареєструватися та перемогти!»" if required_vip else "🔔 «До старту блиц-турніру залишилось 20 хвилин. Запис відкритий!»")
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Register", callback_data=BlitzRegisterCallback(blitz_id=blitz_id).pack())]
        ])
        for character in filtered_characters:
            await _send_message(character, text, reply_markup=markup)

    async def remind(self):
        now = datetime.now()
        today_start = self.blitz_start_at

        vip_remind_time = today_start - timedelta(minutes=self.remind_for_vip_users)
        simple_remind_time = today_start - timedelta(minutes=self.remind_for_simple_users)

        characters = await CharacterService.get_all_characters_where_end_training()

        if now < vip_remind_time:
            await asyncio.sleep((vip_remind_time - now).total_seconds())
            await self.__reminder_blitz_for_users(characters, True, self.blitz_id)
        elif now < today_start:
            await self.__reminder_blitz_for_users(characters, True, self.blitz_id)

        now = datetime.now()

        if now < simple_remind_time:
            await asyncio.sleep((simple_remind_time - now).total_seconds())
            await self.__reminder_blitz_for_users(characters, False, self.blitz_id)
        elif now < today_start:
            await self.__reminder_blitz_for_users(characters, False, self.blitz_id)

        now = datetime.now()
        if now < today_start:
            await asyncio.sleep((today_start - now).total_seconds())
        characters = await BlitzRegisterService.get_characters_from_blitz_character(self.blitz_id)
        for character in characters:
            await _send_message(character, "🚀 «Турнір почався! Граємо 1/8 фіналу!»")
