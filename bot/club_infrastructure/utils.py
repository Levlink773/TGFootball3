from typing import Tuple

from database.models.character import Character
from database.models.club_infrastructure import ClubInfrastructure

from services.club_infrastructure_service import ClubInfrastructureService

from .types import (
    InfrastructureLevel, 
    InfrastructureType, 
    NameInfrastructureType,
    InfrastructureTyping
)
from .config import INFRASTRUCTURE_BONUSES

def _calculate_bonus(procent_bonus: int, *values: int) -> Tuple[int]:
    multiplier = 1 + procent_bonus / 100 
    return tuple(int(value * multiplier) for value in values)

def calculate_bonus_by_infrastructure(
    club_infrastructure: ClubInfrastructure,
    type_infrastructure: NameInfrastructureType | InfrastructureType,
    *_values: int
) -> Tuple[int]:
    if type(type_infrastructure) != InfrastructureType:
        type_infrastructure: InfrastructureType = InfrastructureTyping.get_type(type_infrastructure)

    level_infrastructure: InfrastructureLevel = club_infrastructure.get_infrastructure_level(type_infrastructure)
    procent_bonus = INFRASTRUCTURE_BONUSES[type_infrastructure].get(level_infrastructure)
    return _calculate_bonus(procent_bonus, *_values)

async def calculate_bonus_by_character(
    character: Character,
    type_infrastructure: NameInfrastructureType | InfrastructureType,
    *_values: int
) -> Tuple[int]:
    
    if character.club_id is None:
        return tuple(_values)
    
    club_infrastructure: ClubInfrastructure = await ClubInfrastructureService.get_infrastructure(
        club_id=character.club_id
    )
    
    return calculate_bonus_by_infrastructure(club_infrastructure, type_infrastructure, *_values)
