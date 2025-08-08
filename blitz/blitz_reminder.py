import asyncio
from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from blitz.blitz_match.constans import START_BLITZ_PHOTO, REGISTER_BLITZ_PHOTO
from blitz.services.blitz_service import BlitzService
from blitz.services.message_sender.blitz_sender import send_message_all_characters
from bot.callbacks.blitz_callback import BlitzRegisterCallback
from database.models.blitz import Blitz
from database.models.character import Character
from services.character_service import CharacterService

START_TOURNAMENT = """
🚀 <b>БЛІЦ-ТУРНІР РОЗПОЧИНАЄТЬСЯ!</b> 🚀

📣 Ласкаво просимо на найшвидший і найзапекліший турнір дня! Сьогодні о 15:00 32 учасники (16 команд по 2 гравці) вийшли на поле, щоб вибороти звання чемпіона блиц-турніру.

⚙️ Механіка коротка, але яскрава:
– 5 хвилин 7 вирішальних моментів  
– 30 секунд на атаку  
– Донат енергії X5  

Зараз формується список команд і незабаром ви дізнаєтеся своїх напарників.  

⏳ Через хвилину почнеться 1/8 фіналу – будьте готові до блискавичної боротьби й точних ударів!  
Удачі всім і нехай сильніші здобудуть перемогу! 💥
            """
MSG_VIP_USER = '''
⏰ <b>БЛІЦ-ТУРНІР СТАРТУЄ СЬОГОДНІ О 15:00!</b> ⏰

Не пропусти свій шанс — натискай на кнопку <b>«Зареєструватись 💪»</b> і покажіть, що ви не просто гравець — ви лідер, стратег і легенда турніру!💥 🏆
'''
MSG_SIMPLE_USER = '''
🔔 БЛІЦ-ТУРНІР СЬОГОДНІ О 15:00 🔔

⏳ Залишилось 20 хвилин до старту.
🎯 Натискай <b>«Зареєструватись 💪»</b> та готуйся до блискавичних поєдинків! ⚽️
Запис відкритий!
'''

class BlitzReminder:
    def __init__(self,
                 blitz: Blitz,
                 remind_for_simple_users: int = 20,
                 remind_for_vip_users: int = 30,
                 necessary_count_users: int = 32,
                 register_photo_path: str = REGISTER_BLITZ_PHOTO
                 ):
        self.blitz_start_at = blitz.start_at
        self.blitz_id = blitz.id
        self.remind_for_simple_users = remind_for_simple_users
        self.remind_for_vip_users = remind_for_vip_users
        self.necessary_count_users = necessary_count_users
        self.register_photo_path = register_photo_path

    async def __reminder_blitz_for_users(self, characters: list[Character], required_vip: bool, blitz_id: int):
        filtered_characters = [
            character for character in characters
            if character.vip_pass_is_active == required_vip
        ]
        if not filtered_characters:
            return
        text = MSG_VIP_USER if required_vip else MSG_SIMPLE_USER
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Зареєструватись 💪",
                                  callback_data=BlitzRegisterCallback(blitz_id=blitz_id, max_characters=self.necessary_count_users).pack())]
        ])
        await send_message_all_characters(filtered_characters, text, reply_markup=markup, photo_path=self.register_photo_path)

    async def remind(self) -> bool:
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
        characters = await BlitzService.get_characters_from_blitz_character(self.blitz_id)
        if len(characters) == self.necessary_count_users:
            await send_message_all_characters(characters, START_TOURNAMENT, photo_path=START_BLITZ_PHOTO)
        else:
            cancel_blitz_text = '''
<b>На жаль, на цей бліц-турнір не з'явилось достатньої кількості гравці!</b>

❌ Гра не відбулася.

🔜 <b>Не засмучуйся!</b> Тренуйся та готуйся до наступних битв. Твої перемоги ще попереду!

⚽️ Залишайся з нами, новий бліц-турнір вже скоро, а саме завтра о 15:00!
            '''
            await send_message_all_characters(characters, cancel_blitz_text)
            return False
        return True
