# from datetime import datetime

# from sqlalchemy import select, or_

# from database.models.league_fight import LeagueFight

# from database.session import get_session

# from logging_config import logger
# from constants import (
#     START_DAY_BEST_20_CLUB_LEAGUE,
#     END_DAY_BEST_20_CLUB_LEAGUE
# )

# class Best20ClubLeagueService:
#     # @classmethod
#     # async def get_top_20_club_matches(self) -> list[LeagueFight]:
#     #     now = datetime.now()
#     #     start_date = now.replace(day=START_DAY_BEST_20_CLUB_LEAGUE, hour=0)
#     #     end_date = now.replace(day=END_DAY_BEST_20_CLUB_LEAGUE, hour=23)

        
#     #     async for session in get_session():
#     #         async with session.begin():
#     #             stmt =  (
#     #                 select(LeagueFight)
#     #                 .where(LeagueFight.is_top_20_club == True)
#     #                 .filter(LeagueFight.time_to_start >= start_date)
#     #                 .filter(LeagueFight.time_to_start <= end_date)
#     #             )
                

#     #             result = await session.execute(stmt)
#     #             return result.unique().scalars().all()
            
            
#     # @classmethod
#     # async def my_club_in_top_20_club_league(cls, club_id: int):
#     #     async for session in get_session():
#     #         async with session.begin():             
#     #             now = datetime.now()
#     #             start_date = now.replace(day=4, hour=0, minute=0, second=0, microsecond=0)
#     #             end_date = now.replace(day=20, hour=23, minute=59, second=59, microsecond=999999)
                
#     #             stmt = select(LeagueFight).filter(
#     #                 (LeagueFight.first_club_id == club_id) | 
#     #                 (LeagueFight.second_club_id == club_id),
#     #                 LeagueFight.is_top_20_club == True,
#     #                 LeagueFight.time_to_start >= start_date,
#     #                 LeagueFight.time_to_start <= end_date
#     #             )
#     #             result = await session.execute(stmt)
#     #             return result.scalars().first()
                

                
#     # @classmethod
#     # async def get_next_top_20_league_fight_by_club(cls, club_id: int) -> LeagueFight | None:
#     #     today = datetime.now()

#     #     async for session in get_session():
#     #         async with session.begin():
#     #             try:
#     #                 next_fight = await session.execute(
#     #                     select(LeagueFight)
#     #                     .where(
#     #                         LeagueFight.time_to_start > today,
#     #                         or_(
#     #                             LeagueFight.first_club_id == club_id,
#     #                             LeagueFight.second_club_id == club_id
#     #                         )
                        
#     #                     )
#     #                     .where(LeagueFight.is_top_20_club == True)
#     #                     .order_by(LeagueFight.time_to_start.asc())
#     #                     .limit(1)
#     #                 )
#     #                 result = next_fight.scalars().first()
#     #                 return result
#     #             except Exception as e:
#     #                 print(f"Ошибка при получении следующего матча для команди {club_id}: {e}")
#     #     return None
                
    
#     # @classmethod
#     # async def get_my_league_top_20_club(cls, club_id: int):
#     #     today = datetime.now().date()
#     #     async for session in get_session():
#     #         async with session.begin():
#     #             try:
#     #                 league_fights = await session.execute(
#     #                     select(LeagueFight)
#     #                     .where(
#     #                             LeagueFight.time_to_start >= today,
#     #                         or_(
#     #                             LeagueFight.first_club_id == club_id,
#     #                             LeagueFight.second_club_id == club_id
#     #                         )
#     #                     )
#     #                     .where(LeagueFight.is_top_20_club == True)
#     #                     .order_by(LeagueFight.time_to_start.asc())
#     #                 )
#     #                 return league_fights.scalars().all()
#     #             except Exception as e:
#     #                 print(f"Ошибка при получении следующего матча для команди {club_id}: {e}")
#     #                 return None
    
    
#     # @classmethod
#     # async def get_end_last_match(cls) -> LeagueFight:
#     #     now = datetime.now()
#     #     start_date = now.replace(day=4, hour=0, minute=0, second=0, microsecond=0)
#     #     end_date = now.replace(day=20, hour=23, minute=59, second=59, microsecond=999999)
#     #     async for session in get_session():
#     #         async with session.begin():
#     #             try:
#     #                 stmt = select(LeagueFight).filter(
#     #                 LeagueFight.is_top_20_club == True,
#     #                 LeagueFight.group_id == "LAST_MATCH",
#     #                 LeagueFight.time_to_start >= start_date,
#     #                 LeagueFight.time_to_start <= end_date
#     #             )
                    
#     #                 result = await session.execute(stmt)
#     #                 return result.scalar_one_or_none()
#     #             except Exception as e:
#     #                 logger.error(f"Ошибка при получении последнего матча: {e}")
#     #     return None