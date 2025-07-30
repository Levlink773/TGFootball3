import calendar
from datetime import datetime

from database.models.league_fight import LeagueFight
from database.session import get_session
from sqlalchemy import select, or_, and_, func, case, desc

from database.models.club import Club


class BestLeagueService:
    pass

                        
                
    # @classmethod
    # async def get_best_league(cls) -> list[LeagueFight]:
    #     now = datetime.now()
    #     last_day = calendar.monthrange(now.year, now.month)[1]

    #     start_date = now.replace(day=21, hour=0, minute=0, second=0, microsecond=0)
    #     end_date = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
        
    #     async for session in get_session():
    #         async with session.begin():
    #             stmt =  (
    #                 select(LeagueFight)
    #                 .filter(LeagueFight.time_to_start >= start_date)
    #                 .filter(LeagueFight.time_to_start <= end_date)
    #                 .filter(LeagueFight.is_beast_league == True)
    #             )
                
    #             result = await session.execute(stmt)
    #             return result.unique().scalars().all()
            
            
    # @classmethod
    # async def my_club_in_beast_league(cls, club_id: int):
    #     async for session in get_session():
    #         async with session.begin():             
    #             now = datetime.now()
    #             last_day = calendar.monthrange(now.year, now.month)[1]
    #             start_date = now.replace(day=21, hour=0, minute=0, second=0, microsecond=0)
    #             end_date = now.replace(day=last_day, hour=23, minute=59)
                
    #             stmt = select(LeagueFight).filter(
    #                 (LeagueFight.first_club_id == club_id) | 
    #                 (LeagueFight.second_club_id == club_id),
    #                 LeagueFight.is_beast_league == True,
    #                 LeagueFight.time_to_start >= start_date,
    #                 LeagueFight.time_to_start <= end_date
    #             )
    #             result = await session.execute(stmt)
    #             return result.scalars().first()
                
        
    # @classmethod
    # async def get_next_league_fight_by_club(cls, club_id: int):
    #     today = datetime.now()

    #     async for session in get_session():
    #         async with session.begin():
    #             try:
    #                 next_fight = await session.execute(
    #                     select(LeagueFight)
    #                     .where(
    #                         LeagueFight.time_to_start > today,
    #                         or_(
    #                             LeagueFight.first_club_id == club_id,
    #                             LeagueFight.second_club_id == club_id
    #                         )
                        
    #                     )
    #                     .where(LeagueFight.is_beast_league == True)
    #                     .order_by(LeagueFight.time_to_start.asc())
    #                     .limit(1)
    #                 )
    #                 result = next_fight.scalars().first()
    #                 return result
    #             except Exception as e:
    #                 print(f"Ошибка при получении следующего матча для команди {club_id}: {e}")
    #                 return None
                