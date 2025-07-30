import random
from datetime import datetime, timedelta
from uuid import uuid4

from services.club_service import ClubService
from services.league_services.league_service import LeagueService

from bot.club_infrastructure.distribute_points.add_points_from_league import AddPointsToClub
from bot.club_infrastructure.distribute_points.scheduler_distribute_points import ShedulerdistributePoints

from constants_leagues import TypeLeague

from .distribute_group_clubs import DistributeMatches
from .score_clubs import ScoreClub
from constants import START_DAY_DEFAULT_LEAGUE

class CreateDefaultLeagueMatches:

    @property
    def start_date(self) -> datetime:
        return datetime.now().replace(day = START_DAY_DEFAULT_LEAGUE)        
    
    @property
    def random_group_id(self) -> int:
        return random.randint(1,100000)
    
    async def create_default_league_matches(self) -> None:

        all_clubs = await ClubService.get_all_clubs()
        score_clubs = await ScoreClub(all_clubs).get_score_clubs()
        groups_club_ids = await DistributeMatches(score_clubs).get_groups()
        await self.create_matches_group(groups_club_ids)
    
    async def create_matches_group(self, groups_club_ids:list[int]): 
        for group_club_id in groups_club_ids:
            matches_group = self._generate_matches(group_club_id)
            await self._save_matches(matches_group)

    def _generate_matches(self, club_ids: list[int]):
        num_clubs = len(club_ids)
        schedule = []
        
        for _ in range(num_clubs - 1):
            daily_matches = [(club_ids[i], club_ids[num_clubs - i - 1]) for i in range(num_clubs // 2)]
            schedule.append(daily_matches)
            club_ids = [club_ids[0]] + [club_ids[-1]] + club_ids[1:-1]
        
        return schedule
    
    async def _save_matches(self, matches_group: list[int]):
        group_id = self.random_group_id
        match_dates = [
            self.start_date + timedelta(days=i) 
                for i in range(len(matches_group))
        ]
        for day, match_date in enumerate(match_dates):
            for _, (first_club_id, second_club_id) in enumerate(matches_group[day]):
                
                start_time_fight = datetime.combine(match_date, datetime.min.time()).replace(hour=21)
                
                await LeagueService.create_league_fight(
                    match_id=str(uuid4()),
                    first_club_id=first_club_id,
                    second_club_id=second_club_id,
                    time_to_start=start_time_fight,
                    group_id = group_id,
                    type_league=TypeLeague.DEFAULT_LEAGUE
                )
        else:
            points_manager = AddPointsToClub(
                group_ids   = [group_id],
                type_league = TypeLeague.DEFAULT_LEAGUE,
            )
            sheduler = ShedulerdistributePoints(
                time_distribute = start_time_fight + timedelta(minutes = 5),
                points_manager  = points_manager
            )
            await sheduler.start_wait_distribute_points()
            