import asyncio
from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from blitz.blitz_match.constans import START_BLITZ_PHOTO, REGISTER_BLITZ_PHOTO
from blitz.services.blitz_service import BlitzService
from blitz.services.message_sender.blitz_sender import send_message_all_characters
from bot.callbacks.blitz_callback import BlitzRegisterCallback
from database.models.blitz import Blitz
from database.models.character import Character
from logging_config import logger
from services.character_service import CharacterService


class BlitzTextGetter:

    def __init__(self, start_time: str, count_users: int):
        self.start_time = start_time
        self.count_users = count_users
        self.count_team = count_users // 2

    def start_tournament(self):
        return f"""
🚀 <b>БЛІЦ-ТУРНІР РОЗПОЧИНАЄТЬСЯ!</b> 🚀

📣 Ласкаво просимо на найшвидший і найзапекліший турнір дня! Сьогодні о {self.start_time} {self.count_users} учасники ({self.count_team} команд по 2 гравці) вийшли на поле, щоб вибороти звання чемпіона блиц-турніру.

⚙️ Механіка коротка, але яскрава:
– 5 хвилин 7 вирішальних моментів  
– 30 секунд на атаку  
– Донат енергії X5  

Зараз формується список команд і незабаром ви дізнаєтеся своїх напарників.  

⏳ Через хвилину почнеться 1/8 фіналу – будьте готові до блискавичної боротьби й точних ударів!  
Удачі всім і нехай сильніші здобудуть перемогу! 💥
            """

    def msg_vip_user(self):
        return f'''
⏰ <b>БЛІЦ-ТУРНІР СТАРТУЄ СЬОГОДНІ О {self.start_time}!</b> ⏰

Не пропусти свій шанс — натискай на кнопку <b>«Зареєструватись 💪»</b> і покажіть, що ви не просто гравець — ви лідер, стратег і легенда турніру!💥 🏆
'''

    def msg_simple_user(self):
        return f'''
🔔 БЛІЦ-ТУРНІР СЬОГОДНІ О {self.start_time} 🔔

⏳ Залишилось 20 хвилин до старту.
🎯 Натискай <b>«Зареєструватись 💪»</b> та готуйся до блискавичних поєдинків! ⚽️
Запис відкритий!
'''


class BlitzReminder:
    def __init__(self,
                 blitz: Blitz,
                 remind_for_simple_users: int = 20,
                 remind_for_vip_users: int = 30,
                 remind_else_users: int = 15,
                 necessary_count_users: int = 32,
                 register_photo_path: str = REGISTER_BLITZ_PHOTO
                 ):
        self.blitz_start_at = blitz.start_at
        time_str = self.blitz_start_at.strftime("%H:%M")
        self.blitz_text_getter = BlitzTextGetter(time_str, necessary_count_users)
        self.remind_else = remind_else_users
        self.blitz_id = blitz.id
        self.remind_for_simple_users = remind_for_simple_users
        self.remind_for_vip_users = remind_for_vip_users
        self.necessary_count_users = necessary_count_users
        self.register_photo_path = register_photo_path

    async def __reminder_for_unregistered_users(self, blitz_id: int):
        # Все персонажи, которые могут участвовать
        all_characters = await CharacterService.get_all_characters_where_end_training()
        # Уже зарегистрированные
        registered_characters = await BlitzService.get_characters_from_blitz_character(blitz_id)
        registered_ids = {c.id for c in registered_characters}

        # Фильтруем только тех, кто еще не зарегался
        unregistered_characters = [c for c in all_characters if c.id not in registered_ids]

        if not unregistered_characters:
            return

        text = f'''
⏳ <b>До старту блиц-турніру залишилось {self.remind_else} хвилин!</b>

Не втрать шанс — турнір сьогодні о {self.blitz_text_getter.start_time}.
Натискай <b>«Зареєструватись 💪»</b> прямо зараз, щоб встигнути приєднатись! ⚡️
'''
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Зареєструватись 💪",
                                  callback_data=BlitzRegisterCallback(blitz_id=blitz_id,
                                                                      max_characters=self.necessary_count_users).pack())]
        ])

        await send_message_all_characters(unregistered_characters, text, reply_markup=markup,
                                          photo_path=self.register_photo_path)

    async def __reminder_blitz_for_users(self, characters: list[Character], required_vip: bool, blitz_id: int):
        filtered_characters = [
            character for character in characters
            if character.vip_pass_is_active == required_vip
        ]
        if not filtered_characters:
            return
        text = self.blitz_text_getter.msg_vip_user() if required_vip else self.blitz_text_getter.msg_simple_user()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Зареєструватись 💪",
                                  callback_data=BlitzRegisterCallback(blitz_id=blitz_id,
                                                                      max_characters=self.necessary_count_users).pack())]
        ])
        await send_message_all_characters(filtered_characters, text, reply_markup=markup,
                                          photo_path=self.register_photo_path)

    async def remind(self) -> bool:
        now = datetime.now()
        today_start = self.blitz_start_at
        vip_remind_time = today_start - timedelta(minutes=self.remind_for_vip_users)
        simple_remind_time = today_start - timedelta(minutes=self.remind_for_simple_users)
        else_remind_time = today_start - timedelta(minutes=self.remind_else)

        characters = await CharacterService.get_all_characters_where_end_training()

        # VIP напоминание
        if now < vip_remind_time:
            await asyncio.sleep((vip_remind_time - now).total_seconds())
            await self.__reminder_blitz_for_users(characters, True, self.blitz_id)
        elif now < today_start:
            await self.__reminder_blitz_for_users(characters, True, self.blitz_id)

        now = datetime.now()

        # Simple users напоминание
        if now < simple_remind_time:
            await asyncio.sleep((simple_remind_time - now).total_seconds())
            await self.__reminder_blitz_for_users(characters, False, self.blitz_id)
        elif now < today_start:
            await self.__reminder_blitz_for_users(characters, False, self.blitz_id)

        now = datetime.now()

        # Напоминание всем, кто еще не зарегистрировался (за 15 минут)
        if now < else_remind_time:
            await asyncio.sleep((else_remind_time - now).total_seconds())
            await self.__reminder_for_unregistered_users(self.blitz_id)
        elif now < today_start:
            await self.__reminder_for_unregistered_users(self.blitz_id)

        now = datetime.now()
        if now < today_start:
            await asyncio.sleep((today_start - now).total_seconds())
        characters = await BlitzService.get_characters_from_blitz_character(self.blitz_id)
        logger.info(f"Ch len: {len(characters)}")
        logger.info(f"Need len: {self.necessary_count_users}")
        logger.info(f"Blitz id: {self.blitz_id}")
        if len(characters) >= self.necessary_count_users:
            characters = characters[:self.necessary_count_users]
            logger.info(f"Ch len 1: {len(characters)}")
            await send_message_all_characters(characters, self.blitz_text_getter.start_tournament(),
                                              photo_path=START_BLITZ_PHOTO)
        else:
            cancel_blitz_text = f'''
<b>На жаль, на цей бліц-турнір не з'явилось достатньої кількості гравці!</b>

{len(characters)} / {self.necessary_count_users}

❌ Гра не відбулася.

🔜 <b>Не засмучуйся!</b> Тренуйся та готуйся до наступних битв. Твої перемоги ще попереду!

⚽️ Залишайся з нами, новий бліц-турнір вже скоро, а саме завтра о 15:00!
            '''
            await send_message_all_characters(characters, cancel_blitz_text)
            return False
        return True
