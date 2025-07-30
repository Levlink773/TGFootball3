import random
import asyncio
from asyncio import Task

from typing import Tuple

from .core_duel import Duel
from .types import DuelData, DuelUser, RoleDuel
from training.core.training import Training


class CreateDuel:
    
    def create_duel(self, user_id: int, training: Training) -> Duel:
        return Duel(
            duel_data = self._create_duel_data(user_id),
            training = training
        )
        
    def _create_duel_data(self, user_id: int) -> DuelData:
        user_1, user_2 = self._create_duel_users(user_id)
        return DuelData(
            user_1 = user_1,
            user_2 = user_2
        )
        
    def _create_duel_users(self, user_id: int) -> Tuple[DuelUser, DuelUser]:
        role_user1 = RoleDuel.get_random_role()
        role_user2 = role_user1.toggle()
        user_1 = DuelUser(
            user_id = user_id,
            pvp_role = role_user1,
            is_bot=False
        )

        user_2 = DuelUser(
            user_id = self.random_user_id,
            pvp_role = role_user2,
            is_bot=True
        )
        return user_1, user_2
        
    @property
    def random_user_id(self) -> int:
        return random.randint(6000, 10000)
    
    

class DuelManager:
    active_duels: dict[str, Duel] = {}
    active_task_duel: dict[str, Task] = {}
    creators_duel = CreateDuel()

    @classmethod
    def get_duel(cls, duel_id: str) -> Duel:
        return cls.active_duels.get(duel_id, False)

    @classmethod
    async def create_duel(cls, user_id: int, training: Training) -> Duel:
        duel: Duel = cls.creators_duel.create_duel(user_id, training)
        cls.active_duels[duel.duel_id] = duel
        cls.active_task_duel[duel.duel_id] = asyncio.create_task(duel.start_duel())
        return duel
        
    @classmethod
    async def end_duel(cls, duel_id: str) -> None:
        del cls.active_duels[duel_id]
        cls.active_task_duel[duel_id].cancel()
        del cls.active_task_duel[duel_id]
        
    @classmethod
    async def end_all_duels(cls) -> None:
        for duel_id in list(cls.active_duels.keys()):
            await cls.end_duel(duel_id)
        
        
