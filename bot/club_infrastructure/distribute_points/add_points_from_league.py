from collections import defaultdict
from typing import Optional

from bot.club_infrastructure.config import POINTS_FROM_DISTRIBUTE_FROM_LEAGUE

from database.models.league_fight import LeagueFight
from database.models.club import Club

from services.club_infrastructure_service import ClubInfrastructureService
from services.league_services.default_league_service import LeagueService
from services.league_services.top_20_club_league_service import Top20ClubLeagueService

from constants_leagues import TypeLeague
from best_club_league.types import LeagueRanking


class AddPointsToClub:
    _map_points_club = POINTS_FROM_DISTRIBUTE_FROM_LEAGUE
    other_points = 5

    def __init__(
        self, 
        group_ids: list[str],
        type_league: TypeLeague,
        league_ranking: Optional[LeagueRanking] = None
    ) -> None:

        self.group_ids = group_ids
        self.type_league = type_league
        self.league_ranking = league_ranking

        self.matches: list[LeagueFight] = []

    @property
    def rating_points(self) -> list[int]:
        if self.type_league == TypeLeague.BEST_LEAGUE:
            return self._map_points_club[self.type_league][self.league_ranking]
        return self._map_points_club[self.type_league]

    async def add_points(self) -> None:
        for group_id in self.group_ids:
            matches = await LeagueService.get_month_league_by_group(
                group_id=group_id
            )
            self.matches.extend(matches)
        first_place_club_id = None
        second_place_club_id = None
        if self.type_league == TypeLeague.TOP_20_CLUB_LEAGUE:
            last_match = await Top20ClubLeagueService.get_end_match()
            if last_match:
                first_place_club_id = last_match.winner.id
                second_place_club_id = last_match.loser.id

        rating_clubs = self.get_rating_club_in_matches(
            first_place_club_id, second_place_club_id
        )
        await self.distribute_points(rating_clubs)

    async def distribute_points(self, rating_clubs: dict[int, list[Club]]) -> None:
        for position, clubs in rating_clubs.items():
            for club in clubs:
                if position > 3:
                    points = self.other_points
                else:
                    points = self.rating_points[position - 1]
                if not club.is_fake_club:
                    await ClubInfrastructureService.add_points(
                        club_id=club.id,
                        points=points
                    )

    def get_rating_club_in_matches(
        self,
        first_place_club_id: Optional[int] = None,
        second_place_club_id: Optional[int] = None
    ) -> dict[int, list[Club]]:

        rating_dict = defaultdict(list)
        club_ids_set = set()

        for match in self.matches:
            if match.first_club.id not in club_ids_set:
                rating_dict[match.total_points_first_club].append(
                    match.first_club
                )
                club_ids_set.add(match.first_club.id)
            if match.second_club.id not in club_ids_set:
                rating_dict[match.total_points_second_club].append(
                    match.second_club
                )
                club_ids_set.add(match.second_club.id)

        sorted_points = sorted(
            rating_dict.items(), key=lambda x: x[0], reverse=True
        )
        result = {}
        if first_place_club_id is not None:
            result[1] = [
                club for club in self.matches
                if club.id == first_place_club_id
            ]
            result[2] = [
                club for club in self.matches
                if club.id == second_place_club_id
            ]
  
        start_number = 1 if first_place_club_id is None else 3
 
        for num, (points, clubs) in enumerate(sorted_points, start=start_number):
            result[num] = clubs

        return result


