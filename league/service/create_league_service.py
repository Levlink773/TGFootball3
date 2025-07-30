from database.models.league_fight import LeagueFight
from database.session import get_session
from sqlalchemy import update
from sqlalchemy import select, or_, and_, func
from datetime import datetime, timedelta

from constants_leagues import TypeLeague


class CreateLeagueService:
    
    @staticmethod
    def first_day_last_month() -> datetime:
        today = datetime.now()
        first_day_current_month = today.replace(day=1)
        last_day_last_month = first_day_current_month - timedelta(days=1)
        return last_day_last_month.replace(day=1)

    @staticmethod
    def last_day_last_month() -> datetime:
        today = datetime.now()
        first_day_current_month = today.replace(day=1)
        return first_day_current_month - timedelta(days=1)
    
    
    @classmethod
    async def get_last_months_matches(
        cls, 
        type_league: TypeLeague
    ) -> list[LeagueFight]:
        
        async for session in get_session():
            async with session.begin(): 
                
                query = select(LeagueFight).filter(
                    and_(
                        LeagueFight.time_to_start >= cls.first_day_last_month(),
                        LeagueFight.time_to_start <= cls.last_day_last_month()
                    )
                )
                query = query.filter(LeagueFight.type_league == type_league)
                query = query.order_by(
                    LeagueFight.time_to_start.desc()
                )    
                result = await session.execute(query)
                return result.unique().scalars().all()