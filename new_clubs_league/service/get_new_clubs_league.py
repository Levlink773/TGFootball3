from datetime import datetime, timedelta

from database.models.league_fight import LeagueFight
from database.models.club import Club

from best_club_league.utils.league_create_match import (
    generate_matches_club
)

from services.league_services.new_clubs_league_service import NewClubsLeagueService
from services.league_service import LeagueFightService
from services.club_service import ClubService

from constants_leagues import config_new_club_league
from constants_leagues import TypeLeague

from uuid import uuid4

class NewClubLeaguRepository:
        
    TYPE_LEAGUE = TypeLeague.NEW_CLUB_LEAGUE
        
    async def get_matches(self) -> list[LeagueFight]:    
        new_club_league = await NewClubsLeagueService.get_month_league()
        if not new_club_league:
            await self.generate_matches()
            new_club_league = await NewClubsLeagueService.get_month_league()
        
        return new_club_league
        

    async def generate_matches(self):
        all_clubs = await ClubService.get_all_clubs()
        self.all_clubs = sorted(
            all_clubs,
            key=lambda entry: entry.total_power,
            reverse=True
        )
        start_index = config_new_club_league.START_CLUB_INDEX
        end_index = start_index + config_new_club_league.COUNT_CLUB_IN_GROUP
        for _ in range(config_new_club_league.COUNT_GROUP):
            group_clubs = self.all_clubs[start_index:end_index]
            if len(group_clubs) < config_new_club_league.COUNT_CLUB_IN_GROUP:
                break
            await self.create_matches(
                group_clubs = group_clubs,
            )
            start_index = end_index
            end_index = start_index + config_new_club_league.COUNT_CLUB_IN_GROUP

    
    async def create_matches(
        self, 
        group_clubs: list[Club],
    ) -> None:
        
        matches_group:list[list[Club]] = generate_matches_club(clubs = group_clubs)
        start_date_match = datetime.now().replace(
            hour = config_new_club_league.HOUR_TIME_START_MATCH, 
            minute = 0, 
            second= 0
        )
        for match in matches_group:
            group_id = str(uuid4())[:8]
            await self.create_matches_day(
                clubs_match_day=match,
                date_match=start_date_match,
                group_id=group_id
            )
            start_date_match = start_date_match + timedelta(days=1)
        # else:
        #     points_manager = AddPointsToClub(
        #         group_ids      = [group],
        #         type_league    = TypeLeague.BEST_LEAGUE,
        #         league_ranking = group
        #     )
        #     sheduler = ShedulerdistributePoints(
        #         time_distribute= start_date_match + timedelta(days=1, minutes = 5),
        #         points_manager  = points_manager
        #     )
        #     await sheduler.start_wait_distribute_points()
            
        
    async def create_matches_day(
        self, 
        clubs_match_day: list[list[Club]],
        date_match: datetime,
        group_id: str
    ) -> None:
        
        for match in clubs_match_day:
            match_id = str(uuid4())
            
            await LeagueFightService.create_league_fight(
                match_id = match_id,
                first_club_id  = match[0].id,
                second_club_id = match[1].id,
                time_to_start = date_match,
                group_id = group_id,
                type_league= self.TYPE_LEAGUE,
            )
            

