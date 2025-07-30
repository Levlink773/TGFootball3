from datetime import datetime, timedelta
from collections import defaultdict
from uuid import uuid4

from database.models.league_fight import LeagueFight
from database.models.club import Club

from services.league_services.league_service import LeagueService
from services.league_services.top_20_club_league_service import Top20ClubLeagueService

from constants import END_DAY_BEST_20_CLUB_LEAGUE
from constants_leagues import TypeLeague

class GenerateLastMatchService:
    
    def __init__(self):
        self.fight_top_20_club: list[LeagueFight] = []
    
    async def get_top_2_club(self) -> list[int]:
        self.fight_top_20_club = await Top20ClubLeagueService.get_month_league()
        club_points = defaultdict(int)
        for match in self.fight_top_20_club:
            club_points[match.first_club_id] += match.total_points_first_club
            club_points[match.second_club_id] += match.total_points_second_club
        return [club_id for club_id, _ in sorted(club_points.items(), key=lambda x: x[1], reverse=True)[:2]]
    
    async def get_last_match(self) -> LeagueFight:
        club_ids_winners: list[int] = await self.get_top_2_club()
        match_id = str(uuid4())
        return await LeagueService.create_league_fight(
                match_id = match_id,
                first_club_id  = club_ids_winners[0],
                second_club_id = club_ids_winners[1],
                time_to_start = self.end_match_time,
                group_id = "LAST_MATCH",
                type_league= TypeLeague.TOP_20_CLUB_LEAGUE,
            )
        
    @property
    def end_match_time(self) -> datetime:
        return datetime.now().replace(
            day = END_DAY_BEST_20_CLUB_LEAGUE,
            hour = 17,
            minute = 0,
        )
    
    @property
    def all_clubs(self) -> list[Club]:
        clubs = []
        clubs_ids = set()
        for match in self.fight_top_20_club:
            if match.first_club_id not in clubs_ids:
                clubs.append(match.first_club)
                clubs_ids.add(match.first_club_id)
            if match.second_club_id not in clubs_ids:
                clubs.append(match.second_club)
                clubs_ids.add(match.second_club_id)
        return clubs