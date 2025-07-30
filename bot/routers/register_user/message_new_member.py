import asyncio
from aiogram import Bot

from loader import bot
from logging_config import logger
from database.models.character import Character
from services.character_service import CharacterService

from .constans import ADITIONAL_INFO_PHOTO

TEXT_TEMPLATE_NEW_USER = """
<b>⚽️ Привіт у TG Футболі!</b>
Ти тільки почав — і це круто! Тут ти граєш за свого футболіста, прокачуєш його і ведеш до великої кар’єри 💥

Ось що треба знати з самого старту:

🏋️‍♂️ <b>Тренуйся на Головній площі</b> — чим більше тренувань, тим сильніший твій гравець
👨‍🏫<b> Хочеш більше бонусів? </b>Проходь персональні тренування з тренером (3 рази на день, за ключі)
🎓<b> Не забувай забирати досвід і монети в Навчальному центрі</b> — кожні 12 годин

<b>🕘 Матчі — щодня о 21:00</b>
Щоб ти та твоя команда перемогла — приходь на Стадіон і додавай енергію під час ударів.
✅ Результат матчу залежить від тих, хто реально грає!

🤝 Матчі доступні тільки якщо ти в команді —
Можеш створити свою або приєднатися до іншої.

🔗 І головне — якщо щось незрозуміло, ми завжди поруч:
<a href="https://t.me/tgfootballchat">💬 TG Football чат — пиши тут</a>
"""

TEXT_TEMPLATE_ADD_MONEY = """
🎉 ПОДАРУНОК 30 МОНЕТ ВЖЕ В ТЕБЕ!

-На старті ми даруємо тобі 30 монет 🪙 — витрать їх на перше екіпірування!

Заглянь у Торговий квартал - магазин речей 🛍 — там знайдеш:
👕 форму
👟 бутси
🧤 шорти та гетри.
Кожна річ підсилює твого гравця 💪
"""

class SendMessageNewMember:
    _bot: Bot = bot
    
    def __init__(
        self, 
        character: Character
    ):
        self.character = character
        self.user_id = character.characters_user_id
        
    @classmethod
    async def send_message(cls, character: Character):
        instance = cls(character)
        asyncio.create_task(instance._await())
    
    async def _await(self):
        await asyncio.sleep(30*60)
        await self._send_message(TEXT_TEMPLATE_NEW_USER)
        await asyncio.sleep(60*60)
        await self._send_message(TEXT_TEMPLATE_ADD_MONEY)
        await CharacterService.update_money_character(
            self.character.id,30            
        )
        
    async def _send_message(self, text):
        try:
            await self._bot.send_photo(
                photo=ADITIONAL_INFO_PHOTO,
                chat_id=self.user_id,
                caption=text,
                disable_notification=True
            )
        except Exception as e:
            logger.error(f"Error sending message to {self.user_id}: {e}")
        