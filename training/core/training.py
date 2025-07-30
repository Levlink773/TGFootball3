from datetime import datetime

from aiogram import Bot
from loader import bot

from training.types import Stage, TextParamsTraning
from training.utils.get_params_by_stage import GetParams
from training.utils.text_stage import TextStage, TEXT_TRAINING

from bot.training.keyboard.training import next_stage_keyboard

class Training:
    
    _bot: Bot = bot
    
    
    def __init__(
        self,
        user_id: int,
        character_id: int,
        range_training_times: list[datetime, datetime]
    ) -> None:
        
        self.user_id = user_id
        self.character_id = character_id
        
        self.range_training_times = range_training_times 
        self._start_time: datetime = range_training_times[0]
        self._end_time: datetime = range_training_times[1]
        
        
        self.stage: Stage = Stage.STAGE_1
        self.score: int = 0
        
    @property
    def end_time_from_keyboard(self) -> int:
        return int(self._end_time.timestamp())
        
    def update_stage(self, stage: Stage) -> None:
        self.stage = stage
        
    def add_score_points(self, points: int) -> int:
        self.score += points
        return self.score
    
    async def send_message_by_stage(self) -> None:
        if self.stage == Stage.STAGE_1:
            await self._send_start_training()
        text_params: TextParamsTraning = await GetParams.get_params_epizode(
            stage=self.stage,
        ) 
        await self._send_mesaage_stage(text_params=text_params)
        
    async def _send_mesaage_stage(self, text_params: TextParamsTraning):
        text_etap = TextStage.get_text(text_params)
        text_etap += f"\n\nВаш поточний рахунок за тренування: <b>{self.score}</b> очок. ✴️"

        if text_params.patch_to_photo:
            return await self.__send_photo_stage(
                text_params = text_params,
                text_etap = text_etap
            )
            
        return await self.__send_message_stage(
            text_etap = text_etap
        )
        
    async def __send_photo_stage(
        self, 
        text_params: TextParamsTraning,
        text_etap: str
    ):
        await self._bot.send_photo(
            chat_id=self.user_id,
            photo=text_params.photo,
            caption=text_etap,
            reply_markup=next_stage_keyboard(
                current_stage = self.stage,
                end_time_health = self.end_time_from_keyboard

            )
        )
        
    async def __send_message_stage(
        self, 
        text_etap: str
    ):
        await self._bot.send_message(
            chat_id=self.user_id,
            text=text_etap,
            reply_markup=next_stage_keyboard(
                current_stage = self.stage,
                end_time_health = self.end_time_from_keyboard
            )
        )

    async def _send_start_training(self):
        await self._bot.send_message(
            chat_id=self.user_id,
            text=TEXT_TRAINING.TRAINING_REWARDS_INFO
        )