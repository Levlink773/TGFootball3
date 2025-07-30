from aiogram.filters.callback_data import CallbackData

from bot.club_infrastructure.types import InfrastructureType

class SelectMenuInfrastructure(CallbackData, prefix = "menu_infrastructure"):
    character_is_owner: bool

class SelectInfrastructure(CallbackData, prefix = "infrastructure"):
    infrastructure: InfrastructureType
    is_owner: bool
    
class UpdateInfrastructure(CallbackData, prefix = "update_infrastructure"):
    infrastructure: InfrastructureType