from database.models.duel import Duel

from database.session import get_session
from sqlalchemy.future import select
from sqlalchemy import func, update
from typing import Dict, List

from datetime import datetime
    
from logging_config import logger

from constants import DUEL_START_DAY_SEASON, DUEL_END_DAY_SEASON


class DuelService:
    
    @classmethod
    async def create_duel(cls, 
                          duel_id: str, user_1_id: int, 
                          user_2_id: int, point_user_1: int,
                          point_user_2: int, bit_user_1: int,
                          bit_user_2: int) -> Duel:
        
        async for session in get_session():
            async with session as sess:  
                try:
                    
                    if not (datetime.now().day >= DUEL_START_DAY_SEASON) and not (DUEL_START_DAY_SEASON <= DUEL_END_DAY_SEASON): 
                        return
                    
                    new_duel  = Duel(
                        duel_id      = duel_id,
                        user_1_id    = user_1_id,
                        user_2_id    = user_2_id,
                        point_user_1 = point_user_1,
                        point_user_2 = point_user_2,
                        bit_user_1   = bit_user_1,
                        bit_user_2   = bit_user_2
                                      )
                    sess.add(new_duel)
                    await sess.commit()
                    return new_duel
                except Exception as E:
                    logger.error(f"err create payment: {E}")
                    
    @classmethod
    async def get_season_duels(cls) -> list[Duel]:
        current_time = datetime.now()
        
        season_start_time = datetime(year=current_time.year, month=current_time.month, day=DUEL_START_DAY_SEASON)
        season_end_time   = datetime(year=current_time.year, month=current_time.month, day=DUEL_END_DAY_SEASON)
        
        async for session in get_session():
            async with session.begin():
                try:
                    league_fights = await session.execute(
                        select(Duel).where(
                            Duel.created_time >= season_start_time,
                            Duel.created_time <= season_end_time
                        )
                    )
                    return league_fights.scalars().all()
                except Exception as E:
                    logger.error(f"Err get sesason duels: {E}")
                    
    @classmethod
    async def get_duel_by_id(cls, duel_id: str) -> Duel:
        async for session in get_session():
            async with session.begin():
                try:
                    duel = await session.execute(
                        select(Duel).where(
                            Duel.duel_id == duel_id
                        )
                    )
                    return duel.scalar_one_or_none()
                except Exception as E:
                    logger.error(f"Err get sesason duels: {E}")
                    