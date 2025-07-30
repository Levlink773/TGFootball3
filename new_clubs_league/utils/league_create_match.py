from database.models.club import Club

from league.utils import LeagueService

def generate_matches_club(clubs: list[Club]) -> list[list[Club]]:
    matchs = LeagueService.generate_round_robin_schedule(
        clubs = clubs
    )
    return matchs    

def generate_club_group(top_league_clubs: list[Club]):
    for i in range(0, len(top_league_clubs), 8):
        clubs = top_league_clubs[i:i + 8]
        yield clubs
