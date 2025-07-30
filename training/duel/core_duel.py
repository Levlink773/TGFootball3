import asyncio

from training.constans import (
    PERIOD_STAGE,
    PERIOD_STAGE_FIGHT_DUEL,
    TIMES_SLEEP_ENTRY_DATA_DUEL,
    SCORE_WINNER_DUEL_STAGE
)
from training.core.training import Training
from .types import DuelData, DuelUser
from .duel_sender import DuelSender

class Duel:    
    
    def __init__(self, duel_data: DuelData, training: Training) -> None:
        self.duel_data = duel_data
        self.duel_sender = DuelSender(self.duel_data, training)
        self.training = training
            
        self._user_1 = duel_data.user_1
        self._user_2 = duel_data.user_2
            
    @property
    def duel_id(self) -> str:
        return self.duel_data.duel_id
            
    async def start_duel(self):
        for _ in range(PERIOD_STAGE):
            await self.duel_sender.send_message_role()
            await asyncio.sleep(2)
            await self._start_stage()
            self.duel_data.change_roles_character()
        await self.duel_sender.send_end_training_duel()

    async def _start_stage(self):
        for _ in range(PERIOD_STAGE_FIGHT_DUEL):
            await self.duel_sender.send_message_select_angle()
            await self._wait_select_angle()    
            winner_stage_user = self._choice_winner_stage()
            if not winner_stage_user.is_bot:
                self.training.add_score_points(points=SCORE_WINNER_DUEL_STAGE)
                winner_stage_user.add_points(SCORE_WINNER_DUEL_STAGE)
            await self.duel_sender.send_itogs_etap(winner_stage_user)
            
    async def _wait_select_angle(self):
        await asyncio.sleep(TIMES_SLEEP_ENTRY_DATA_DUEL)
        if self.duel_data.user_1.position_angle is None:
            self.duel_data.user_1.select_random_angle()
            
        if self.duel_data.user_2.position_angle is None:
            self.duel_data.user_2.select_random_angle()
        
    def _choice_winner_stage(self) -> DuelUser:
        if self._user_1.position_angle == self._user_2.position_angle:
            return  self.duel_data.goalkepper
        return self.duel_data.forward