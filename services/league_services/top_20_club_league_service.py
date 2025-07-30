from typing import Optional
from sqlalchemy import select, or_

from constants_leagues import TypeLeague, GetConfig

from database.models.league_fight import LeagueFight
from database.session import get_session

from .league_service import LeagueService


class Top20ClubLeagueService(LeagueService):
    type_league = TypeLeague.TOP_20_CLUB_LEAGUE
    config = GetConfig.get_config(TypeLeague.TOP_20_CLUB_LEAGUE)
    
    @classmethod
    async def get_end_match(cls) -> Optional[LeagueFight]:
        async for session in get_session():
            async with session.begin():
                stmt = (
                    select(LeagueFight)
                    .where(LeagueFight.type_league == cls.type_league)
                    .filter(LeagueFight.time_to_start >= cls.config.DATETIME_START_LEAGUE)
                    .filter(LeagueFight.time_to_start <= cls.config.DATETIME_END_LEAGUE)
                )
                result = await session.execute(stmt)
                return result.scalar_one_or_none()