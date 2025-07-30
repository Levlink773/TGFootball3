import asyncio
from aiogram import Router
from aiogram.types import CallbackQuery

from database.models.character import Character

from bot.training.callbacks.training_callbacks import SelectAngleTrainingDuel
from bot.training.filter.get_training import GetTraining
from bot.training.filter.training_is_active import TrainingIsActive
from bot.training.filter.get_duel import GetDuelData

from training.duel.duel_manager import DuelManager
from training.core.manager_training import TrainingManager
from training.duel.types import DuelData
from training.duel.types import PositionAngle

training_duel_router = Router()

async def start_duel_training(
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
        "⌛ Через 5 секунд розпочнеться дуель! Приготуйтеся до гри та будьте готові зробити вибір!"
    )
    await asyncio.sleep(5)   
    await message.delete()
    
    await DuelManager.create_duel(character.characters_user_id, training)
    
    
@training_duel_router.callback_query(
    SelectAngleTrainingDuel.filter(),
    GetTraining(),
    TrainingIsActive(),
    GetDuelData()
)
async def incorrect_direction(
    query: CallbackQuery,
    callback_data: SelectAngleTrainingDuel,
    duel_data: DuelData,
    character: Character
):    
    text_stage = {
        PositionAngle.LEFT: "Вліво",
        PositionAngle.RIGHT: "Вправо",
        PositionAngle.UP: "Вгору"
    }
    
    await query.message.edit_reply_markup(
        reply_markup = None
    )
    user = duel_data.get_user_by_id(character.characters_user_id)
    user.position_angle = callback_data.angle
    await query.answer(
        text = f"Ви вибрали напрямок: {text_stage[callback_data.angle]}"
    )