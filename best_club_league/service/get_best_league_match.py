from collections import defaultdict
from datetime import datetime, timedelta

from database.models.league_fight import LeagueFight
from database.models.club import Club

from bot.club_infrastructure.distribute_points.add_points_from_league import AddPointsToClub
from bot.club_infrastructure.distribute_points.scheduler_distribute_points import ShedulerdistributePoints

from bot.utils.get_top_24_club_by_league import get_top_24_clubs
from best_club_league.types import LeagueRanking
from best_club_league.utils.league_create_match import (
    generate_club_group,
    generate_matches_club)

from services.league_services.default_league_service import DefaultLeagueService 
from services.league_services.best_league_service import BestLeagueService
from services.league_services.league_service import LeagueService
from services.league_services.top_20_club_league_service import Top20ClubLeagueService

from constants_leagues import TypeLeague


from uuid import uuid4

class BestClubLeagueMatchService:
    
    def getname(self, league: list[LeagueFight]):
        
        club_names = set()
        for fight in league:
            club_names.add(fight.first_club.name_club)
            club_names.add(fight.second_club.name_club)
        
        for club in club_names:
            print(club)
        
    async def get_matches(self) -> list[LeagueFight]:    
        best_club_league = await BestLeagueService.get_month_league()
        if not best_club_league:
            await self.generate_matches()
            best_club_league = await BestLeagueService.get_month_league()
        
        return best_club_league
        
    async def get_top_clubs(self) -> dict[int, dict]:

        default_league = await DefaultLeagueService.get_month_league()
        sorted_default_league = get_top_24_clubs(default_league)
        top_20_club_league = await Top20ClubLeagueService.get_month_league()
        sorted_top_20_club_league = get_top_24_clubs(top_20_club_league)

        all_clubs = sorted_default_league + sorted_top_20_club_league
        club_data = defaultdict(lambda: {'club': None, 'points': 0})

        club_data = defaultdict(lambda: {
            'club': None,
            'club_id': 0,
            'club_name': '',
            'points': 0,
            'goals_scored': 0,
            'goals_conceded': 0,
            'goal_difference': 0,
            'total_power': 0,
        })

        for entry in all_clubs:
            club_id = entry['club_id']
            data = club_data[club_id]

            if data['club'] is None:
                data['club'] = entry['club']
                data['club_id'] = club_id
                data['club_name'] = entry['club_name']
                data['total_power'] = entry['total_power']

            data['points'] += entry['points']
            data['goals_scored'] += entry['goals_scored']
            data['goals_conceded'] += entry['goals_conceded']
            data['goal_difference'] += entry['goal_difference']
        sorted_rankings = dict(
            sorted(club_data.items(), key=lambda item: item[1]['points'], reverse=True)
        )
        return [club['club'] for _,club in sorted_rankings.items()][:24]
        
    async def generate_matches(self):
        top_clubs = await self.get_top_clubs()
        group_generator = generate_club_group(top_clubs)
        for group in LeagueRanking:
            group_clubs = next(group_generator)
            await self.create_matches(
                group_clubs = group_clubs,
                group       = group
            )   
    
    async def create_matches(
        self, 
        group_clubs: list[Club],
        group: LeagueRanking
    ) -> None:
        
        matches_group:list[list[Club]] = generate_matches_club(clubs = group_clubs)
        start_date_match = datetime.now().replace(hour = 21, minute = 0, second= 0 )
        for match in matches_group:
            await self.create_matches_day(
                clubs_match_day = match,
                date_match      = start_date_match,
                group           = group
            )
            start_date_match = start_date_match + timedelta(days=1)
        else:
            points_manager = AddPointsToClub(
                group_ids      = [group],
                type_league    = TypeLeague.BEST_LEAGUE,
                league_ranking = group
            )
            sheduler = ShedulerdistributePoints(
                time_distribute= start_date_match + timedelta(days=1, minutes = 5),
                points_manager  = points_manager
            )
            await sheduler.start_wait_distribute_points()
            
        
    async def create_matches_day(
        self, 
        clubs_match_day: list[list[Club]],
        date_match: datetime,
        group: LeagueRanking
    ) -> None:
        
        for match in clubs_match_day:
            match_id = str(uuid4())
            
            await LeagueService.create_league_fight(
                match_id = match_id,
                first_club_id  = match[0].id,
                second_club_id = match[1].id,
                time_to_start = date_match,
                group_id = group.value,
                type_league=TypeLeague.BEST_LEAGUE,
            )
            

