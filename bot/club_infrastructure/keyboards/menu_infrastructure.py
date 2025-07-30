from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.club_infrastructure.callbacks.infrastructure_callbacks import (
    SelectInfrastructure,
    UpdateInfrastructure
)
from bot.club_infrastructure.types import InfrastructureType

def menu_infrastructure(is_owner: bool):
    keyboard = InlineKeyboardBuilder()
    
    for infrastructure in InfrastructureType:
        keyboard.button(
            text = infrastructure.value,
            callback_data = SelectInfrastructure(
                infrastructure = infrastructure,
                is_owner = is_owner
            )
        )
    
    keyboard.button(text="🎖 Розподілення поінтів", callback_data="info_desrtibute_club_points")
    return keyboard.adjust(2,2,2,1).as_markup()
        

def update_level_infrastructure(
    infrastructure: InfrastructureType, 
):
    return (
        InlineKeyboardBuilder()
        .button(
            text = "⭐️ Покращити рівень",
            callback_data = UpdateInfrastructure(
                infrastructure = infrastructure
            )
        )
        .adjust(1)
        .as_markup()
    )