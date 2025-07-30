from datetime import datetime

from sqlalchemy import select, or_

from constants_leagues import TypeLeague, GetConfig

from database.models.league_fight import LeagueFight
from database.session import get_session

from .league_service import LeagueService


class DefaultLeagueService(LeagueService):
    type_league = TypeLeague.DEFAULT_LEAGUE
    config = GetConfig.get_config(TypeLeague.DEFAULT_LEAGUE)
    
    
