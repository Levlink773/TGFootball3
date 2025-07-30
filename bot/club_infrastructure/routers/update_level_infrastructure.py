from aiogram import Router
from aiogram.types import CallbackQuery

from bot.club_infrastructure.callbacks.infrastructure_callbacks import (
    UpdateInfrastructure,
    SelectInfrastructure
)
from bot.club_infrastructure.config import UPGRADE_COSTS
from bot.club_infrastructure.types import InfrastructureTyping, InfrastructureLevel
from bot.club_infrastructure.filters.get_club_and_infrastructure import GetClubAndInfrastructure
from bot.filters.check_admin_club_filter import CheckOwnerClub

from database.models.club_infrastructure import ClubInfrastructure

from services.club_infrastructure_service import ClubInfrastructureService

from .select_infrastructure import select_infrastructure_handler

update_level_infrastructure_router = Router()


@update_level_infrastructure_router.callback_query(
    UpdateInfrastructure.filter(),
    GetClubAndInfrastructure(),
    CheckOwnerClub()
)
async def update_level_infrastructure_handler(
    query: CallbackQuery,
    callback_data: UpdateInfrastructure,
    club_infrastructure: ClubInfrastructure
):
    infrastructure_level: InfrastructureLevel = club_infrastructure.get_infrastructure_level(
        infrastructure_type = callback_data.infrastructure
    )
    if infrastructure_level == InfrastructureLevel.LEVEL_5:
        return await query.answer(
            text = "Максимальний рівень",
            show_alert = True
        )
    next_level = infrastructure_level.get_next_level()
        
    cost = UPGRADE_COSTS[next_level]
    if cost > club_infrastructure.points:
        return await query.answer(
            text = "Недостатньо коштів на балансі клуба",
            show_alert = True
        )
    
    await ClubInfrastructureService.update_level_infrastructure(
        club_id = club_infrastructure.club_id,
        infrastructure_type  = InfrastructureTyping.get_name(callback_data.infrastructure),
        infrastructure_level = next_level
    )
    await ClubInfrastructureService.reduce_points(
        club_id = club_infrastructure.club_id,
        points = cost
    )
    await query.answer(
        text = "Успішно оновлено",
        show_alert = True
    )
    await query.message.delete()
    club_infrastructure = await ClubInfrastructureService.get_infrastructure(
        club_id = club_infrastructure.club_id
    )
    
    await select_infrastructure_handler(
        query = query,
        callback_data = SelectInfrastructure(
            infrastructure = callback_data.infrastructure,
            is_owner = True
        ),
        club_infrastructure = club_infrastructure
    )