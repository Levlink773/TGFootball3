from typing import List, Tuple
from database.models.club import Club

class LeagueService:

    @staticmethod
    def generate_round_robin_schedule(clubs: List['Club']) -> List[List[Tuple['Club', 'Club']]]:
        num_clubs = len(clubs)
        if num_clubs % 2 != 0:
            clubs.append(None)

        num_days = num_clubs - 1
        half_size = num_clubs // 2

        schedule = []

        for day in range(num_days):
            daily_matches = []
            for i in range(half_size):
                club1 = clubs[i]
                club2 = clubs[num_clubs - i - 1]
                if club1 is not None and club2 is not None:
                    daily_matches.append((club1, club2))
            schedule.append(daily_matches)
            clubs = [clubs[0]] + [clubs[-1]] + clubs[1:-1]

        return schedule
