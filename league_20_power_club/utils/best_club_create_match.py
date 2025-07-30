from database.models.club import Club

from league.utils import LeagueService
from services.club_service import ClubService

from typing import Generator

def generate_matches_club(clubs: list[Club]) -> list[list[Club]]:
    matchs = LeagueService.generate_round_robin_schedule(
        clubs = clubs
    )
    return matchs    

def generate_club_group(top_league_clubs: list[Club]):
    for i in range(0, len(top_league_clubs), 10):
        clubs = top_league_clubs[i:i + 10]
        yield clubs

async def get_top_20_club() -> list[Club]:
    all_clubs = await ClubService.get_all_clubs()
    clubs = sorted(all_clubs, key=lambda entity: getattr(entity, "total_power"), reverse=True)
    return clubs[:20] 