import asyncio
import random
from time import time

from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery

from database.models.character import Character

from bot.training.callbacks.training_callbacks import QTECallback
from bot.training.keyboard.qte_keyboard import get_qte_keyboard 
from bot.training.filter.get_training import GetTraining
from bot.training.filter.training_is_active import TrainingIsActive

from services.training_service import TrainingService

from training.core.manager_training import TrainingManager
from training.core.training import Training  
from training.types import Stage
from training.constans import (
    COUNT_QTE_STAGES, 
    DIRECTIONS,
    BASE_SCORE_QTE,
    MIN_SCORE,
    PENALTY_STEP,
    PENALTY_VALUE
)

qte_router = Router()

async def start_qte_training(
    query: CallbackQuery,
    character: Character
):
    training = TrainingManager.get_training(
        user_id = character.characters_user_id,
    )
    if not training:
        return await query.message.answer(
            text = "Тренування не знайдено"
        )
    training.update_stage(
        stage = training.stage.next_stage()
    )
    
    message = await query.message.answer(
        "Через 5 секунд почнеться QTE гра, вам потрібно буде вибрати правильний напрямок"
    )
    await asyncio.sleep(5)   
    await message.delete()
    
    correct_direction = random.choice(DIRECTIONS)
    await query.message.answer(
        f"Натисніть на: {correct_direction}",
        reply_markup=get_qte_keyboard(
            correct_direction=correct_direction,
            shuffle = False,
            stage = 1,
            end_time_health = training.end_time_from_keyboard
        )
    )
    
@qte_router.callback_query(
    QTECallback.filter(F.direction != F.correct_direction),
    GetTraining(),
    TrainingIsActive()
)
async def incorrect_direction(
    query: CallbackQuery,
):
    await query.answer(
        text = "Неправильний напрямок"
    )

@qte_router.callback_query(
    QTECallback.filter(
        F.stage == COUNT_QTE_STAGES
    ),
    TrainingIsActive(),
    GetTraining()
)
async def stop_qte(
    query: CallbackQuery,
    training: Training
):
    await query.message.edit_reply_markup(
        reply_markup=None
    )
    if training.stage != Stage.STAGE_DUEL:
        training.update_stage(
                stage = training.stage.next_stage()
            )
    await training.send_message_by_stage()


@qte_router.callback_query(
    QTECallback.filter(),
    GetTraining(),
    TrainingIsActive()
)
async def correct_direction(
    query: CallbackQuery,
    callback_data: QTECallback,
    character: Character,
    training: Training
):
    
    points = calculate_qte_score(callback_data.timestamp)
    training.add_score_points(points = points)
    await query.answer(
        text = f"Правильний напрямок, ви отримали {points} очок."
    )
    await TrainingService.update_score_user(
        user_id = character.characters_user_id,
        score = training.score
    )
    
    current_direction = random.choice(DIRECTIONS)
    await query.message.edit_text(
        f"Натисніть на: {current_direction}",
        reply_markup=get_qte_keyboard(
            correct_direction=current_direction,
            shuffle = True,
            stage = callback_data.stage + 1,
            end_time_health = training.end_time_from_keyboard
        )
    )
    
def calculate_qte_score(timestamp: float) -> int:
    elapsed_time = time() - timestamp  
    if elapsed_time <= 3:
        return int(BASE_SCORE_QTE)  
    else:
        penalty_count = (elapsed_time - 3) // PENALTY_STEP 
        final_score = BASE_SCORE_QTE - (penalty_count * PENALTY_VALUE)
        return max(int(final_score), MIN_SCORE)