from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.models.character import Character
from bot.callbacks.hall_fame_callbacks import SelectHallFamePosition
from bot.keyboards.hall_fame_keyboard import select_position_rating

from utils.hall_fame_utils import get_top_characters_by_position
from constants import HALL_FAME_POSITION_PHOTO

from services.character_service import CharacterService


hall_fame_position_rating_router = Router()

TEXT_HALL_FAME_POSITION = """
🏅 <b>Зал слави - рейтинг гравців</b> 🏅

Оберіть позицію, для якої хочете переглянути рейтинг:  

⚽ <b>Нападники</b> - топ найкращих бомбардирів 🏹  
🎯 <b>Півзахисники</b> - майстри асистів і контролю м'яча 🏋‍♂  
🛡 <b>Захисники</b> - непохитна стіна оборони 🏰  
🧤 <b>Воротарі</b> - кращі голкіпери, що творять дива у воротах 🧱  

🔍 <i>Обери категорію, щоб побачити легенд гри!</i>
"""


@hall_fame_position_rating_router.message(F.text == "👨‍👩‍👦‍👦 Рейтинг позицій")
async def hall_fame_position_handler(
    message: Message,
):
    await message.answer_photo(
        photo   = HALL_FAME_POSITION_PHOTO,
        caption = TEXT_HALL_FAME_POSITION,
        reply_markup = select_position_rating()
    )

@hall_fame_position_rating_router.callback_query(
    SelectHallFamePosition.filter()
)
async def hall_fame_position_rating_handler(
    query: CallbackQuery,
    callback_data: SelectHallFamePosition,
    character: Character
):
    
    position_characters = await CharacterService.get_characters_by_position(
        position = callback_data.position
    )
    
    await query.message.answer(
        text = get_top_characters_by_position(
            all_characters = position_characters,
            my_character = character,
            position = callback_data.position
        )
    )