import random

from datetime import datetime, timedelta
from uuid import uuid4

from bot.club_infrastructure.distribute_points.add_points_from_league import AddPointsToClub
from bot.club_infrastructure.distribute_points.scheduler_distribute_points import ShedulerdistributePoints

from constants import END_DAY_BEST_20_CLUB_LEAGUE
from constants_leagues import TypeLeague

from database.models.league_fight import LeagueFight
from database.models.club import Club

from league_20_power_club.types import LeagueBestClubRanking
from league_20_power_club.utils.best_club_create_match import (
    generate_matches_club, 
    generate_club_group,
    get_top_20_club
) 

# from services.best_20_club_league_service import Best20ClubLeagueService
from services.league_services.top_20_club_league_service import Top20ClubLeagueService
from services.league_services.league_service import LeagueService



class BestClubLeagueMatchService:
 
    async def get_matches(self) -> list[LeagueFight]:    
        best_top_20_club_league = await Top20ClubLeagueService.get_month_league()
        if not best_top_20_club_league:
            await self.generate_top_20_club_matches()
            best_top_20_club_league = await Top20ClubLeagueService.get_month_league()
        
        return best_top_20_club_league
        

        
    async def generate_top_20_club_matches(self):
        top_20_clubs: list[Club] = await get_top_20_club()
        random.shuffle(top_20_clubs)
        group_generator = generate_club_group(top_20_clubs)
        for group in LeagueBestClubRanking:
            group_clubs = next(group_generator)
            await self.create_matches(
                group_clubs = group_clubs,
                group       = group
            )   
        
        points_manager = AddPointsToClub(
            group_ids = [
                LeagueBestClubRanking.GROUP_A.value, 
                LeagueBestClubRanking.GROUP_B.value
            ],
            type_league = TypeLeague.TOP_20_CLUB_LEAGUE,
        )
        sheduler = ShedulerdistributePoints(
            time_distribute= self.end_time_matches,
            points_manager  = points_manager
        )
        await sheduler.start_wait_distribute_points()
        
    @property
    def end_time_matches(self) -> datetime:
        return datetime.now().replace(
            day = END_DAY_BEST_20_CLUB_LEAGUE,
            hour = 16,
            minute = 5,
        )
    
    
    async def create_matches(
        self, 
        group_clubs: list[Club],
        group: LeagueBestClubRanking
    ) -> datetime:
        
        matches_group:list[list[Club]] = generate_matches_club(clubs = group_clubs)
        start_date_match = datetime.now().replace(hour = 17, minute = 0, second= 0 )
        for match in matches_group:
            await self.create_matches_day(
                clubs_match_day = match,
                date_match      = start_date_match,
                group           = group
            )
            start_date_match = start_date_match + timedelta(days=2)
        
    async def create_matches_day(
        self, 
        clubs_match_day: list[list[Club]],
        date_match: datetime,
        group: LeagueBestClubRanking
    ) -> None:
        
        for match in clubs_match_day:
            match_id = str(uuid4())
            
            await LeagueService.create_league_fight(
                match_id = match_id,
                first_club_id  = match[0].id,
                second_club_id = match[1].id,
                time_to_start = date_match,
                group_id = group.value,
                type_league= TypeLeague.TOP_20_CLUB_LEAGUE,
            )
            

