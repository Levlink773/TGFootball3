from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message

from datetime import datetime

from database.models.character import Character

from services.best_club_league import BestLeagueService
from services.league_services.best_league_service import BestLeagueService
from services.league_services.top_20_club_league_service import Top20ClubLeagueService
from services.league_services.new_clubs_league_service import NewClubsLeagueService

from constants_leagues import config_new_club_league

from constants import (
    START_DAY_BEST_LEAGUE,
    END_DAY_BEST_LEAGUE,
    START_DAY_BEST_20_CLUB_LEAGUE,
    END_DAY_BEST_20_CLUB_LEAGUE
)

class UserInClub(BaseFilter):
    
    def __init__(self) -> None:
        pass
        
    async def __call__(self, event: Message, character: Character) -> Any:
        if character.club_id is None:
            await event.answer("Ви не перебуваете в клубі")
            return False
        return True
    
class ClubInBeastLeague(BaseFilter):
    
    def __init__(self) -> None:
        pass
    
    async def __call__(self, event: Message, character: Character) -> Any:
        current_day = datetime.now().day
        
        if not (current_day >= START_DAY_BEST_LEAGUE and current_day <= END_DAY_BEST_LEAGUE):
            return False
        
        club_in_beast_league = await BestLeagueService.my_club_in_league(
            club_id = character.club_id
        )
        
        if not club_in_beast_league:
            return False
        
        return True
        
class ClubIn20PowerLeague(BaseFilter):

    def __init__(self) -> None:
        pass

    async def __call__(self, event: Message, character: Character) -> Any:
        current_day = datetime.now().day

        if not (current_day >= START_DAY_BEST_20_CLUB_LEAGUE and current_day <= END_DAY_BEST_20_CLUB_LEAGUE):
            return False

        club_in_beast_league = await Top20ClubLeagueService.my_club_in_league(
            club_id = character.club_id
        )

        if not club_in_beast_league:
            return False

        return True

class ClubInNewClubLeague(BaseFilter):
    
    async def __call__(self, event: Message, character: Character) -> Any:
        
        if not config_new_club_league.league_is_active:
            return False
    
        club_in_new_club_league = await NewClubsLeagueService.my_club_in_league(
            club_id=character.club_id
        )
        
        if not club_in_new_club_league:
            return False
        
        return True