from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from collections import defaultdict

from database.models.club import Club
from database.models.league_fight import LeagueFight

from services.club_service import ClubService
from services.league_services.league_service import LeagueService

from config import LEAGUES
from loader import bot


class UpdateLeagueRating:

    trigger = CronTrigger(day=1, hour=11, minute=26)

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
    
    
    async def get_top_club_league(self):
        all_fights_in_league: list[LeagueFight] = await LeagueService.get_league_matches_last_month()
        
        groups = defaultdict(list)
        for match in all_fights_in_league:
            groups[match.group_id].append(match)

        group_scores = defaultdict(lambda: defaultdict(int)) 

        for group_id, matches in groups.items():
            for match in matches:
                group_scores[group_id][match.first_club_id] += match.total_points_first_club
                group_scores[group_id][match.second_club_id] += match.total_points_second_club

        top_teams_by_group = {}
        for group_id, scores in group_scores.items():
            sorted_teams = sorted(
                scores.items(),
                key=lambda item: item[1], 
                reverse=True  
            )
          
            top_teams_by_group[group_id] = [
                {"club_id": club_id, "total_points": points}
                for club_id, points in sorted_teams[:3]
            ]

        return top_teams_by_group

    async def _update_rank_league(self, club: Club):
        index_rang_club = LEAGUES.index(club.league)
        if index_rang_club == len(LEAGUES) - 1:
           new_rang_league =  LEAGUES[-1]
        new_rang_league = LEAGUES[index_rang_club + 1]
        await ClubService.update_rang_league(
            club_id = club.id,
            new_rang_league = new_rang_league
        )
        
        
    async def update_rank_league(self, top_teams_by_group: dict):
        for top_teams in top_teams_by_group.values():
            for team in top_teams:
                club = await ClubService.get_club(
                    club_id = team['club_id']
                )
                await self._update_rank_league(club)
                
    async def _start(self):
        top_teams_by_group = await self.get_top_club_league()
        await self.update_rank_league(top_teams_by_group)
        
    async def start(self):
        self.scheduler.add_job(
            self._start,
            self.trigger
        )
        self.scheduler.start()