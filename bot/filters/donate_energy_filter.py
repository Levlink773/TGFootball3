import time
import asyncio

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from database.models.character import Character

from match.constans import TIME_EVENT_DONATE_ENERGY
        
class CheckTimeDonateEnergyMatch(BaseFilter):
    _last_donate_times: dict[int, int] = {}
    _dict_message_alert: dict[int, Message] = {}
    _sleep_time: int = 5

    async def __call__(self, event: CallbackQuery | Message, character: Character) -> bool:
        self._event: Message = event.message if isinstance(event, CallbackQuery) else event
        self._character = character
        
        if not character.club_id:
            return await self._send_message(
                "Ви не перебуваєте в команді, тому ви не можете донатити енергію"
            )

        user_id = character.characters_user_id
        current_time = int(time.time())
        last_donate_time = self._last_donate_times.get(user_id, False)
        
        if last_donate_time:
            if (current_time - last_donate_time) > TIME_EVENT_DONATE_ENERGY:
                try:
                    del self._last_donate_times[user_id]
                    del self._dict_message_alert[user_id]
                except:
                    pass
                finally:
                    return True
            if (current_time - last_donate_time) < self._sleep_time:
                await self._send_message(
                    f"""
Ти вже донатив енергію, почекайте трохи
Ти можешь донатити енергію не частіше ніж раз в <b>{self._sleep_time}</b> секунд
                    """
                )
                return False
        self._last_donate_times[user_id] = current_time
        return True

    async def _send_message(self, message: str) -> None:
        if self._character.characters_user_id in self._dict_message_alert:
            return
        message = await self._event.answer(message)
        self._dict_message_alert[self._character.characters_user_id] = message
        asyncio.create_task(self.__del_message(message))

    async def __del_message(self, message: Message) -> None:
        try:
            await asyncio.sleep(self._sleep_time)
            await message.delete()
            del self._dict_message_alert[self._character.characters_user_id]
        except:
            pass