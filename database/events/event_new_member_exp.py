import asyncio

from datetime import datetime

from aiogram import Bot
from aiogram.types import FSInputFile 

from bot.routers.stores.box.open_box import OpenBoxService

from database.models.character import Character
from database.models.types import TypeBox

from services.character_service import CharacterService

from loader import bot
from constants import lootboxes

from .base_event import BaseEventListener

DATE_CONSTANT = datetime(2025,4,25, 0, 0, 0)
EXP_CONSTANT = 20
TYPE_BOX_NEW_MEMBER = TypeBox.NEW_MEMBER_BOX 
PHOTO_BOX_NEW_MEMBER = FSInputFile("src/new_member_get_bonus.png")
semaphore = asyncio.Semaphore(1) 


TEMPLATE_OPEN_BOX = """
💡 <b>Ти зробив перший крок</b> — отримав EXP і розблокував <b>Бокс новачка</b>!

Всередині тебе чекає:
⚡ <b>Енергія</b> ({min_energy}–{max_energy}) — для тренувань та матчів  
💰 <b>Гроші</b> ({min_money}–{max_money}) — на перші апґрейди  
🧠 <b>Досвід</b> ({min_exp}–{max_exp}) — для наступного рівня  

<b>Прокачка почалась. Далі — більше!</b> 🚀
"""

class NewMemberExpEventListener(BaseEventListener):
    _bot: Bot = bot

    async def handle_event(self, character: Character) -> None:
        async with semaphore:
            if character.time_get_member_bonus:
                return
            
            if character.created_at < DATE_CONSTANT:
                return
            
            if character.exp <= EXP_CONSTANT:
                return
            
            box_open_service = OpenBoxService(
                type_box = TYPE_BOX_NEW_MEMBER,
                character = character,
                bot = self._bot         
            )
            await CharacterService.update_get_new_member_bonus(
                character_id = character.id,
            )
        asyncio.create_task(
            self.open_box(box_open_service)
        )

    async def open_box(
        self,
        box_open_service: OpenBoxService,
    ) -> None:
        if not box_open_service:
            raise ValueError("Box open service is not initialized.")
        
        info_lootbox = lootboxes.get(box_open_service.type_box, None)
        if not info_lootbox:
            raise ValueError(f"Invalid lootbox type: {box_open_service.type_box}")
        
        text = TEMPLATE_OPEN_BOX.format(
            min_energy=info_lootbox["min_energy"],
            max_energy=info_lootbox["max_energy"],
            min_money=info_lootbox["min_money"],
            max_money=info_lootbox["max_money"],
            min_exp=info_lootbox["min_exp"],
            max_exp=info_lootbox["max_exp"],
        )
        await self._bot.send_photo(
            photo=PHOTO_BOX_NEW_MEMBER,
            chat_id=box_open_service.character.characters_user_id,
            caption=text
        )
        await box_open_service.open_box()