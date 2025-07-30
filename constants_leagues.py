from abc import ABC

from datetime import datetime
from enum import Enum

from apscheduler.triggers.cron import CronTrigger


class TypeLeague(Enum):
    BEST_LEAGUE = "BEST_LEAGUE"
    DEFAULT_LEAGUE = "DEFAULT_LEAGUE"
    TOP_20_CLUB_LEAGUE = "TOP_20_CLUB_LEAGUE"
    NEW_CLUB_LEAGUE = "NEW_CLUB_LEAGUE"

NAMES_LEAGUES: dict = {
    TypeLeague.BEST_LEAGUE: "👑 ЕвроКубки",
    TypeLeague.DEFAULT_LEAGUE: "⚽ Ліга",
    TypeLeague.TOP_20_CLUB_LEAGUE: "💼 Кубок України",
    TypeLeague.NEW_CLUB_LEAGUE: "🌱 Ліга Новачків"
}


class BaseConfigLeague(ABC):
    DAY_START: int
    DAY_END: int
    HOUR_TIME_START_MATCH: int
    
    @property
    def TRIGGER_START_LEAGUE(self) -> CronTrigger:
        return CronTrigger(
            day=self.DAY_START,
            hour=8,
        )
    
    @property
    def TRIGGER_SEND_MESSAGE_START(self) -> CronTrigger:
        return CronTrigger(
            day=self.DAY_START,
            hour=7,
            minute=0
        )
    
    @property
    def DATETIME_START_LEAGUE(self) -> datetime:
        now = datetime.now()
        return now.replace(
            day=self.DAY_START, 
            hour=8, 
            minute=0
        )
    
    @property
    def DATETIME_END_LEAGUE(self) -> datetime:
        now = datetime.now()
        return now.replace(
            day=self.DAY_END, 
            hour=23, 
            minute=59
        )
        
    @property
    def league_is_active(self) -> bool:
        now = datetime.now()
        return self.DAY_START <= now.day <= self.DAY_END
        
        
class ConfigNewClubLeague(BaseConfigLeague):
    DAY_START = 5
    DAY_END = 15
    HOUR_TIME_START_MATCH = 18

    COUNT_GROUP = 4
    COUNT_CLUB_IN_GROUP = 10
    START_CLUB_INDEX = 21


class ConfigDefaultLeague(BaseConfigLeague):
    DAY_START = 1
    DAY_END = 20
    HOUR_TIME_START_MATCH = 21


class ConfigTop20ClubLeague(BaseConfigLeague):
    DAY_START = 3
    DAY_END = 21
    HOUR_TIME_START_MATCH = 21


class ConfigBestLeague(BaseConfigLeague):
    DAY_START = 21
    DAY_END = 30
    HOUR_TIME_START_MATCH = 21


config_new_club_league = ConfigNewClubLeague()
config_default_league = ConfigDefaultLeague()
config_top_20_club_league = ConfigTop20ClubLeague()
config_best_league = ConfigBestLeague()


class GetConfig:
    configs: dict[TypeLeague, BaseConfigLeague] = {
        TypeLeague.BEST_LEAGUE: config_best_league,
        TypeLeague.TOP_20_CLUB_LEAGUE: config_top_20_club_league,
        TypeLeague.DEFAULT_LEAGUE: config_default_league,
        TypeLeague.NEW_CLUB_LEAGUE: config_new_club_league,
    }
    
    @staticmethod
    def get_config(type_league: TypeLeague) -> BaseConfigLeague:
        return GetConfig.configs[type_league]
