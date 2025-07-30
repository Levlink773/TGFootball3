from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message
from config import ADMINS

class CheckUserIsAdmin(BaseFilter):
    
    async def __call__(self, event: Message) -> Any:
        if event.from_user.id in ADMINS:
            return True
        return False