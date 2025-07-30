from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message
from database.models.character import Character

class CheckDuelStatus(BaseFilter):
    
    def __init__(self) -> None:
        pass
        
    async def __call__(self, event: Message, character: Character) -> Any:
        if character.reminder.character_in_duel:
            await event.answer("❌ <b>Ви вже процессі ПВП-пеналті</b>")
            return False
        return True