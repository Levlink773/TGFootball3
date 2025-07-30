from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime, timedelta

from constants_leagues import TypeLeague, BaseConfigLeague

from database.models.league_fight import LeagueFight


class BaseLeagueService(ABC):
    config: BaseConfigLeague
    type_league: TypeLeague

    @classmethod
    @abstractmethod
    async def get_month_league(
        cls, 
        type_league: TypeLeague
    ) -> Optional[list[LeagueFight]]:
        raise NotImplementedError("This method should be overridden in subclasses")

    @classmethod
    @abstractmethod
    async def my_club_in_league(
        cls,
        type_league: TypeLeague
    ) -> Optional[list[LeagueFight]]:
        raise NotImplementedError("This method should be overridden in subclasses")

    @classmethod
    @abstractmethod
    async def get_next_league_fight_by_club(
        cls, 
        club_id: int,
        type_league: TypeLeague
    ) -> Optional[LeagueFight]:
        raise NotImplementedError("This method should be overridden in subclasses")

    @classmethod
    @property
    def first_day_month(cls) -> datetime:
        return datetime.now().date().replace(day=1)
    

    @classmethod
    @property
    def start_next_month(cls) -> datetime:
        return (
            cls.first_day_month + timedelta(days=32)
        ).replace(day=1)
        
    @classmethod
    @property
    def start_day_last_month(cls) -> datetime:
        return (
            cls.first_day_month - timedelta(days=1)
        ).replace(day=1)
        
    @classmethod
    @property
    def end_day_last_month(cls) -> datetime:
        return (
            cls.first_day_month - timedelta(days=1)
        )