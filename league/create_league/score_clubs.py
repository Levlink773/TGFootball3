from typing import List, Dict
from collections import defaultdict

from database.models.league_fight import LeagueFight
from database.models.club import Club

from league.service.create_league_service import CreateLeagueService
from constants_leagues import TypeLeague

class ScoreClub:
    def __init__(self, all_clubs: List[Club]):
        self.all_clubs = all_clubs
        self.score_clubs = defaultdict(int)
    
    @staticmethod
    def _score_points_from_matches(matches: List[LeagueFight], score_table: Dict[int, int]) -> None:
        for match in matches:
            score_table[match.first_club_id] += match.total_points_first_club
            score_table[match.second_club_id] += match.total_points_second_club
    
    async def _fetch_league_scores(self, league_type: TypeLeague) -> Dict[int, int]:
        score_table = defaultdict(int)
        matches = await CreateLeagueService.get_last_months_matches(type_league=league_type)
        self._score_points_from_matches(matches, score_table)
        return score_table
    
    async def get_score_clubs(self) -> Dict[int, int]:
        self.score_clubs = {club.id: 0 for club in self.all_clubs}
        
        leagues = [
            TypeLeague.DEFAULT_LEAGUE,
            TypeLeague.BEST_LEAGUE,
        ]
        
        for league in leagues:
            league_scores = await self._fetch_league_scores(league)
            for club_id, score in league_scores.items():
                if club_id not in self.score_clubs:
                    continue
                self.score_clubs[club_id] += score
        score_clubs = dict(sorted(self.score_clubs.items(), key=lambda x: x[1], reverse=True)) 
        return score_clubs
