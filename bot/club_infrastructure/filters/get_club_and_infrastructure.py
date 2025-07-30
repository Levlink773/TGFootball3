from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from database.models.character import Character
from database.models.club import Club
from database.models.club_infrastructure import ClubInfrastructure

from services.club_service import ClubService
from services.club_infrastructure_service import ClubInfrastructureService
from typing import Union

class GetClubAndInfrastructure(BaseFilter):

    async def __call__(self, event: Union[Message, CallbackQuery], character: Character) -> Any:
        if character.club_id == None:
            return False
        
        club: Club = await ClubService.get_club(
            club_id = character.club_id
        )
        
        if not club:
            return False
        
        club_infrastructure: ClubInfrastructure = await ClubInfrastructureService.get_infrastructure(
            club_id = character.club_id
        )
        if not club_infrastructure:
            club_infrastructure = await ClubInfrastructureService.create_infrastructure(
                club_id = character.club_id
            )
            
        return {
            "club": club,
            "club_infrastructure" : club_infrastructure
            
        }