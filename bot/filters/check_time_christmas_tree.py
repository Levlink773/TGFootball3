from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import Message

from constants import date_is_get_reward_christmas_tree

class CheckTimeChristmasTree(BaseFilter):

    async def __call__(self, event: Message) -> bool:
        if not date_is_get_reward_christmas_tree():
            await event.answer(
                "Сьогодні не ті дні, коли стоїть новорічна ялинка. "
                "Настрій свята ще попереду або вже залишився позаду, "
                "але зараз час для нових справ і рішень."
            )
            return False
        return True
    
    
