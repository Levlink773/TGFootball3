from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery

from database.models.character import Character

from bot.training.callbacks.training_callbacks import NextStage 
from bot.training.routers.qte_stage import start_qte_training
from bot.training.filter.get_training import GetTraining
from bot.training.filter.training_is_active import TrainingIsActive
from bot.training.routers.duel_stage import start_duel_training

from services.training_service import TrainingService

from training.core.training import Training
from training.core.manager_training import TrainingManager
from training.types import Stage
from training.constans import QTE_STAGES, DUEL_STAGE



answer_etap_router = Router()


@answer_etap_router.callback_query(
    NextStage.filter(),
    GetTraining(),
    TrainingIsActive()
)
async def next_etap_handler(
    query: CallbackQuery,
    callback_data: NextStage,
    character: Character,
    training: Training
):
    stage = callback_data.next_stage   
    await query.message.edit_reply_markup(
        reply_markup = None
    )
    if stage == Stage.END_TRAINIG:
        return await TrainingManager.end_user_training(character.characters_user_id)

    if stage in QTE_STAGES:
        return await start_qte_training(query, character)
    
    if stage in DUEL_STAGE:
        return await start_duel_training(query, character)
    
    training.update_stage(callback_data.next_stage)
    
    score: int = training.add_score_points(callback_data.count_score)
    await query.answer(
        text = f"Ви отримали {callback_data.count_score} балів за цю відповідь",
        cache_time=5
    )
    await TrainingService.update_score_user(
        user_id = character.characters_user_id,
        score = score
    )
    
    await training.send_message_by_stage()