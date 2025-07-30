from aiogram import Router, F
from aiogram.types import Message

from database.models.character import Character

from services.match_character_service import MatchCharacterService
from utils.hall_fame_utils import get_top_mvp_users_ranking


hall_fame_mvp_rating_router = Router()

@hall_fame_mvp_rating_router.message(F.text == "👨‍👩‍👦‍👦 Рейтинг MVP")
async def hall_fame_mvp_handler(
    message: Message,
    character: Character
) -> None:
    
    match_characters = await MatchCharacterService.get_match_characters_by_one_month() 
    text_mvp = await get_top_mvp_users_ranking(
        active_users = match_characters,
        my_character = character
    )

    await message.answer(
        text = text_mvp
    )


