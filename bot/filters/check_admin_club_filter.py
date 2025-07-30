from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from config import ADMINS

from database.models.character import Character
from database.models.club import Club

from services.club_service import ClubService
from typing import Union

class CheckOwnerClub(BaseFilter):
    
    async def __call__(self, event: Union[Message, CallbackQuery], character: Character) -> Any:
        self.type_event = type(event)
        self.event = event
        
        club: Club = await ClubService.get_club(
            club_id = character.club_id
        )
        if not club:
            await self._send_error("Не смог найти клуб")
            return False
        
        if club.owner_id != character.characters_user_id:
            await self._send_error("Вы не админ клуба")
            return False
        
        return True
        
    async def _send_error(self, text: str):
        if self.type_event == Message:
            await self.event.answer(text)

        if self.type_event == CallbackQuery:
            await self.event.answer(text, show_alert=True)