import asyncio
from datetime import timedelta
from typing import Dict

from database.models.character import Character
from ..keyboard.get_new_member_bonus import get_box_new_member
from ..constans import PHOTO_BOX_NEW_MEMBER
from loader import bot


TEXT_TEMLATE_REWARD = """
<b>🎉 Вітаємо, новачок!</b>

Твоя перша нагорода вже тут! 🧰  
Це <b>стартовий кейс</b>, який ти отримав за те, що розпочав свій футбольний шлях! ⚽️

⌛️ Минуло 3 години з моменту реєстрації — а отже, настав час отримати заслужене 🎁

<b>🏆 Натисни кнопку нижче, щоб забрати нагороду!</b>
"""


class GetterLastReward:
    FIRST_WAIT_TIME = timedelta(minutes=5)  
    REPEAT_REMINDER_INTERVAL = timedelta(minutes=5)  

    def __init__(self, character):
        self.character = character
        self.is_get_reward = False
        self._task: asyncio.Task | None = None

    def start(self):
        if self._task is None or self._task.done():
            self.is_get_reward = False
            self._task = asyncio.create_task(self._reward_flow())

    def stop(self):
        self.is_get_reward = True
        if self._task and not self._task.done():
            self._task.cancel()

    async def _reward_flow(self):
        try:
            await asyncio.sleep(self.FIRST_WAIT_TIME.total_seconds())
            if not self.is_get_reward:
                await self.send_initial_reward()

            #while not self.is_get_reward:
            #    await asyncio.sleep(self.REPEAT_REMINDER_INTERVAL.total_seconds())
            #    if not self.is_get_reward:
            #        await self.send_reminder()
        except asyncio.CancelledError:
            pass

    async def send_initial_reward(self):
        await bot.send_photo(
            chat_id=self.character.characters_user_id,
            photo=PHOTO_BOX_NEW_MEMBER,
            caption=TEXT_TEMLATE_REWARD,
            reply_markup=get_box_new_member()
        )

    async def send_reminder(self):
        await bot.send_photo(
            chat_id=self.character.characters_user_id,
            photo=PHOTO_BOX_NEW_MEMBER,
            caption="<b>🎁 Подарунок чекає!</b>\nНе забудь його забрати в меню.",
        )


class RewardManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tasks = {}
        return cls._instance

    def __init__(self):
        self._tasks: Dict[int, GetterLastReward]

    def start(self, character: Character):
        self.stop(character.characters_user_id)
        reward = GetterLastReward(character)
        reward.start()
        self._tasks[character.characters_user_id] = reward

    def mark_as_received(self, user_id: int):
        if user_id in self._tasks:
            self._tasks[user_id].stop()
            del self._tasks[user_id]

    def get_task(self, user_id: int) -> GetterLastReward | None:
        return self._tasks.get(user_id)

    def stop(self, user_id: int):
        if user_id in self._tasks:
            self._tasks[user_id].stop()
            del self._tasks[user_id]
