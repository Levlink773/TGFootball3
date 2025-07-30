from datetime import datetime, timedelta
from typing import Optional, Tuple

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from bot.training.callbacks.training_callbacks import JoinToTraining 
from bot.training.keyboard.buy_training_key import to_menu_buy_training_key

from constants import NEED_TRAINING_KEY

from training.constans import TIME_REGISTER_TRAINING
from training.core.manager_training import TrainingManager

from database.models.character import Character
from database.models.training import CharacterJoinTraining, TrainingTimer

from services.training_service import TrainingService
from services.character_service import CharacterService

from training.constans import (
    MAX_LIMIT_JOIN_CHARACTERS,
    TIME_TRAINING
)
from .utils import get_near_end_time_training


join_trainig_router = Router()

@join_trainig_router.callback_query(
    JoinToTraining.filter(),
)
async def joined_to_training(
    query: CallbackQuery,
    callback_data: JoinToTraining,
    character: Character
):
    join_training = TrainingJoinManager(
        character = character,
        end_time_training = callback_data.end_time_health
    )
    text_join, keyboard = await join_training.join()
    if keyboard:
        return await query.message.answer_photo(
            photo = NEED_TRAINING_KEY,
            caption = text_join,
            reply_markup = keyboard
        )
    await query.answer(
        text = text_join,
        show_alert=True,
        cache_time=5
    )
    
@join_trainig_router.message(
    F.text == "👨🏻‍🏫 Тренування з тренером"
)
async def joined_to_training(
    message: Message,
    character: Character
):
    _text = """
🔑 <b>Ваші ключі: {count}</b>  

Ключі потрібні для участі у тренуваннях. ⚽🏆  
Один ключ = один вхід на тренування.  

⏳ Не забувайте використовувати їх, щоб покращити навички та стати кращим гравцем!  
"""
    
    await message.answer(
        text = _text.format(
            count = character.training_key
        )
    )
    near_end_time_training, is_active = get_near_end_time_training()
    
    if not is_active:
        return await message.answer("Тренування зараз не активне")
    
    join_training = TrainingJoinManager(
        character,
        end_time_training = near_end_time_training
        
    )
    text_join, keyboard = await join_training.join()
    if keyboard:
        return await message.answer_photo(
            photo = NEED_TRAINING_KEY,
            caption = text_join,
            reply_markup = keyboard
        )
    await message.answer(
        text = text_join,
        reply_markup = keyboard
    )
    
    
class TrainingJoinManager:
    def __init__(
        self, 
        character: Character,
        end_time_training: int
    ) -> None:
        
        self.character: Character = character
        self.end_time_training: int = end_time_training
        
        self.user_id: int = character.characters_user_id
        self.joined_user: Optional[CharacterJoinTraining] = None
        self.training_timer: Optional[TrainingTimer] = None

    @property
    def _end_time_training(self) -> datetime:
        return datetime.fromtimestamp(self.end_time_training)

    @property
    def _start_time_register(self) -> datetime:
        return self._end_time_training - TIME_REGISTER_TRAINING - TIME_TRAINING
    
    @property
    def _end_time_register(self) -> datetime:
        return self._end_time_training - TIME_TRAINING

    async def join(self) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        await self._load_training_data()
                
        if self._is_user_already_joined():
            return "Ви вже зареєстровані на тренування", None
    
        if self._is_training_finished():
            return "Тренування завершено", None    
    
        if not self._is_user_already_joined() and self.joined_user:
            if not self._has_training_key():
                return "⚽ <b>Ти вже пройшов тренування, але можеш повернутися ще раз!</b> 🏆\n\n🔑 Вхід можливий лише за ключі. Готовий знову випробувати свої сили?", to_menu_buy_training_key()
            else:
                return await self._start_training_by_key()
        
        if not self._has_training_key():
            return "🔑 Вхід можливий лише за ключі.\n\nГотовий знову випробувати свої сили?", to_menu_buy_training_key()    
        
        if not self._is_registration_open():
            if self.character.training_key > 0:
                return "Не час для реєстрації на тренування, ви зможете почати тренування з наступної сессії", None
            return "Не час для реєстрації на тренування", None
        
        if await self._is_training_full() and not self.character.vip_pass_is_active:
            return "Немає вільних місць на тренування", None

        return await self._register_user()

    async def _load_training_data(self) -> None:
        self.joined_user = await TrainingService.user_is_join_to_training(
            user_id = self.user_id,
            range_training_times = [
                self._start_time_register, self._end_time_training
            ]
        )

    def _is_registration_open(self) -> bool:
        now = datetime.now()
        return self._start_time_register <= now <= self._end_time_register

    def _is_training_finished(self) -> bool:
        return bool(self._end_time_register and self._end_time_training < datetime.now())

    def _has_training_key(self) -> bool:
        return self.character.training_key > 0

    def _is_user_already_joined(self) -> bool:
        return bool(self.joined_user and not self.joined_user.training_is_end)

    async def _is_training_full(self) -> bool:
        joined_users: list = await TrainingService.get_joined_users(
            [self._start_time_register, self._end_time_register]
        )
        return len(joined_users) >= MAX_LIMIT_JOIN_CHARACTERS

    async def _register_user(self) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        await TrainingService.add_character_to_training(
            user_id = self.user_id, 
            character_id = self.character.id
        )
        await CharacterService.remove_training_key(self.character.id)
        return "Ви успішно зареєструвались на тренування", None

    async def _start_training_by_key(self) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        await TrainingManager.start_user_training(
            user_id = self.user_id,
            character_id = self.character.id,
            range_training_times = [
                self._end_time_register, self._end_time_training
            ]
        )
        await CharacterService.remove_training_key(self.character.id)
        await TrainingService.anulate_user_training(self.user_id)
        return "Ви успішно зареєструвались на тренування за ключ", None
