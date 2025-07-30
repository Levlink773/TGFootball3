from aiogram import Router
from aiogram.types import CallbackQuery

from bot.training.callbacks.training_callbacks import SelectStat
from bot.training.filter.training_is_active import TrainingIsActive

from database.models.character import Character

from constants import const_name_characteristics

from services.character_service import CharacterService

from training.utils.text_stage import TEXT_TRAINING

end_training_router = Router() 


@end_training_router.callback_query(
    SelectStat.filter(),
)
async def select_stat_hansler(
    query: CallbackQuery,
    callback_data: SelectStat,
    character: Character,
):  
    
    stat = callback_data.stat
    name_stat = const_name_characteristics[stat]
    await query.message.edit_reply_markup(
        reply_markup = None
    )
    text = TEXT_TRAINING.SUCCES_END_TRAINING.format(
        count_stat = callback_data.count_stat,
        name_stat = name_stat
    )
    await CharacterService.update_character_characteristic(
        character_id = character.id,
        type_characteristic = stat,
        amount_add_points = callback_data.count_stat
    )
    await query.message.answer(
        text = text
    )