from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.models.user_bot import UserBot


class BlockButtonFilter(BaseFilter):
    
    async def __call__(self, event: Message) -> Any:
        if event.text.startswith("🔒"):
            await event.answer("Ця кнопка заблокована, ви не можете її натискати.")
            return False
        return True
