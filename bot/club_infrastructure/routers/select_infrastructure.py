from aiogram import Router
from aiogram.types import CallbackQuery

from bot.club_infrastructure.callbacks.infrastructure_callbacks import (
    SelectInfrastructure
)
from bot.club_infrastructure.config import PHOTOS_INFRASTRUCTURE
from bot.club_infrastructure.keyboards.menu_infrastructure import update_level_infrastructure
from bot.club_infrastructure.filters.get_club_and_infrastructure import GetClubAndInfrastructure
from bot.club_infrastructure.text_config import get_description_infrastructure

from database.models.club_infrastructure import ClubInfrastructure


select_infrastructure_router = Router()

@select_infrastructure_router.callback_query(
    GetClubAndInfrastructure(),
    SelectInfrastructure.filter()
)
async def select_infrastructure_handler(
    query: CallbackQuery,
    callback_data: SelectInfrastructure,
    club_infrastructure: ClubInfrastructure
):
    text = get_description_infrastructure(
        infrastructure_type = callback_data.infrastructure,
        infrastructure_level = club_infrastructure.get_infrastructure_level(
            infrastructure_type = callback_data.infrastructure
        ),
        is_owner = callback_data.is_owner
    )
    keyboard = None
    if callback_data.is_owner:
        keyboard = update_level_infrastructure(
            infrastructure = callback_data.infrastructure
        )
    
    await query.message.answer_photo(
        photo = PHOTOS_INFRASTRUCTURE[callback_data.infrastructure],
        caption = text,
        reply_markup = keyboard
    )