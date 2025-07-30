from datetime import timedelta
from typing import Optional

from database.models.league_fight import LeagueFight

from best_club_league.types import LeagueRanking
from services.league_services.league_service import LeagueService

from logging_config import logger
from constants_leagues import TypeLeague

from .add_points_from_league import AddPointsToClub
from .scheduler_distribute_points import ShedulerdistributePoints


class Waiterdistributer:

    def __init__(self) -> None:
        pass
    
    async def start(self) -> None:
        all_groups_started = await LeagueService.get_latest_fights_from_current_month()
        top_20_groups = []
        for group in all_groups_started:
            if group.type_league == TypeLeague.TOP_20_CLUB_LEAGUE:
                top_20_groups.append(group)
            else:
                await self._distribute_groups(group)
        
        if top_20_groups:
            await self._distribute_top_20_groups(top_20_groups)
    
    async def _distribute_top_20_groups(self, fights: list[LeagueFight]):
        try:
            time_distribute= fights[-1].time_to_start + timedelta(days=1, minutes=3)

            points_manager = AddPointsToClub(
                group_ids   = [fight.group_id for fight in fights],
                type_league = TypeLeague.TOP_20_CLUB_LEAGUE
            )
            
            sheduler = ShedulerdistributePoints(
                time_distribute=time_distribute,
                points_manager=points_manager
            )
            
            await sheduler.start_wait_distribute_points()
        except Exception as E:
            logger.error(E)
    
    
    async def _distribute_groups(self, fight: LeagueFight):
        try:
            time_distribute= fight.time_to_start + timedelta(minutes=3)
            type_league, league_ranking = self.get_type_league(fight)                
            points_manager = AddPointsToClub(
                group_ids      = [fight.group_id],
                type_league    = type_league,
                league_ranking = league_ranking
            )
            
            sheduler = ShedulerdistributePoints(
                time_distribute= time_distribute,
                points_manager  = points_manager
            )
            
            await sheduler.start_wait_distribute_points()
        except Exception as E:
            logger.error(E)
            
    
    def get_type_league(self, fight: LeagueFight) -> TypeLeague | Optional[LeagueRanking]:
        if fight.type_league == TypeLeague.BEST_LEAGUE:
            if fight.group_id == "Ліга Чемпіонів":
                return TypeLeague.BEST_LEAGUE, LeagueRanking.GROUP_A
            elif fight.group_id == "Ліга Європи":
                return TypeLeague.BEST_LEAGUE, LeagueRanking.GROUP_B
            elif fight.group_id == "Ліга Конференції":
                return TypeLeague.BEST_LEAGUE, LeagueRanking.GROUP_C
        
        if fight.type_league == TypeLeague.TOP_20_CLUB_LEAGUE:
            return TypeLeague.TOP_20_CLUB_LEAGUE, None
        
        else:
            return TypeLeague.DEFAULT_LEAGUE, None