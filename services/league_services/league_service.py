from typing import Optional
from datetime import datetime

from sqlalchemy import select, or_, func, desc, over
from sqlalchemy.orm import selectinload
from constants_leagues import TypeLeague, BaseConfigLeague

from database.models.league_fight import LeagueFight
from database.session import get_session

from .base_service import BaseLeagueService


class LeagueService(BaseLeagueService):
    config: BaseConfigLeague
    type_league: TypeLeague
    
    @classmethod
    async def get_month_league(
        cls, 
    ) -> Optional[list[LeagueFight]]:
        async for session in get_session():
            async with session.begin():
                stmt = (
                    select(LeagueFight)
                    .options(selectinload(LeagueFight.first_club)) 
                    .options(selectinload(LeagueFight.second_club)) 
                    .where(LeagueFight.type_league == cls.type_league)
                    .filter(LeagueFight.time_to_start >= cls.config.DATETIME_START_LEAGUE)
                    .filter(LeagueFight.time_to_start <= cls.config.DATETIME_END_LEAGUE)
                    
                )
                result = await session.execute(stmt)
                return result.unique().scalars().all()
           
    @classmethod   
    async def my_club_in_league(
        cls,
        club_id: int
    ) -> Optional[list[LeagueFight]]:
        async for session in get_session():
            async with session.begin():
                stmt = (
                    select(LeagueFight)
                    .filter(
                        (LeagueFight.first_club_id == club_id) | 
                        (LeagueFight.second_club_id == club_id),
                        LeagueFight.type_league == cls.type_league,
                        LeagueFight.time_to_start >= cls.config.DATETIME_START_LEAGUE,
                        LeagueFight.time_to_start <= cls.config.DATETIME_END_LEAGUE
                    )
                )
                result = await session.execute(stmt)
                return result.scalars().first()

    @classmethod
    async def get_next_league_fight_by_club(
        cls, 
        club_id: int,
    ) -> Optional[LeagueFight]:
        
        async for session in get_session():
            async with session.begin():
                stmt = (
                    select(LeagueFight)
                    .where(
                        LeagueFight.time_to_start > datetime.now(),
                        LeagueFight.type_league == cls.type_league,
                        or_(
                            LeagueFight.first_club_id == club_id,
                            LeagueFight.second_club_id == club_id
                        )
                    )
                    .order_by(LeagueFight.time_to_start.asc())
                    .limit(1)
                )
                result = await session.execute(stmt)
                return result.scalars().first()

    @classmethod
    async def get_month_league_by_group(cls, group_id: str) -> Optional[list[LeagueFight]]:
        async for session in get_session():
            async with session.begin():
                stmt = (
                    select(LeagueFight)
                    .where(
                        LeagueFight.group_id == group_id,
                        LeagueFight.time_to_start >= cls.first_day_month,
                        LeagueFight.time_to_start < cls.start_next_month
                    )
                    .order_by(LeagueFight.time_to_start.asc())
                )
                result = await session.execute(stmt)
                return result.unique().scalars().all()
            
    @classmethod
    async def get_month_league_by_club(
        cls,
        club_id: int
    ) -> Optional[list[LeagueFight]]:
        print(cls.first_day_month)
        async for session in get_session():
            async with session.begin():
                stmt = (
                    select(LeagueFight)
                    .where(
                        or_(
                            LeagueFight.first_club_id == club_id,
                            LeagueFight.second_club_id == club_id
                        ),
                        LeagueFight.time_to_start >= cls.first_day_month,
                        LeagueFight.type_league == cls.type_league
                    )
                    .order_by(LeagueFight.time_to_start.asc())
                )
                result = await session.execute(stmt)
                return result.unique().scalars().all()
            
    @classmethod
    async def get_group_id_by_club(cls, club_id: int) -> str | None:
        async for session in get_session():
            async with session.begin():
                league_fight = await session.execute(
                    select(LeagueFight.group_id)
                    .where(
                        or_(
                            LeagueFight.first_club_id == club_id,
                            LeagueFight.second_club_id == club_id
                        ),
                        LeagueFight.time_to_start >= cls.first_day_month,
                        LeagueFight.time_to_start < cls.start_next_month
                    )
                    .limit(1)
                )
                group_id = league_fight.scalar()
                return group_id

    @classmethod
    async def get_group_id_by_club_and_type_league(
        cls,
        club_id: int,
        type_league: TypeLeague
    ) -> str | None:
        async for session in get_session():
            async with session.begin():
                league_fight = await session.execute(
                    select(LeagueFight.group_id)
                    .where(
                        or_(
                            LeagueFight.first_club_id == club_id,
                            LeagueFight.second_club_id == club_id
                        ),
                        LeagueFight.time_to_start >= cls.first_day_month,
                        LeagueFight.time_to_start < cls.start_next_month,
                        LeagueFight.type_league == type_league
                    )
                    .limit(1)
                )
                group_id = league_fight.scalar()
                return group_id

    @classmethod
    async def increment_goal(
        cls, 
        match_id: str, 
        club_id: int, 
        add_goal: int = 1
    ) -> LeagueFight:
        
        async for session in get_session():
            async with session.begin():
                try:
                    league_fight = await session.execute(
                        select(LeagueFight).where(LeagueFight.match_id == match_id)
                    )
                    league_fight_obj = league_fight.scalars().first()

                    if not league_fight_obj:
                        print(f"Матч с ID {match_id} не найден.")
                        return None

                    if league_fight_obj.first_club_id == club_id:
                        league_fight_obj.goal_first_club += add_goal
                    elif league_fight_obj.second_club_id == club_id:
                        league_fight_obj.goal_second_club += add_goal
                    else:
                        print(f"Команда с ID {club_id} не участвует в матче с ID {match_id}.")
                        return None

                    session.add(league_fight_obj)
                    await session.commit()
                    return league_fight_obj
                
                except Exception as e:
                    return None
                
    @classmethod
    async def get_league_fight(cls, match_id: str) -> LeagueFight:
        async for session in get_session():
            async with session.begin():
                stmt = select(LeagueFight).filter_by(match_id = match_id)
                result = await session.execute(stmt)
                club = result.scalar_one_or_none()
                return club
    
    @classmethod
    async def get_match_today(cls, club_id: int) -> Optional[list[LeagueFight]]:
        async for session in get_session():
            async with session.begin():
                stmt = (
                    select(LeagueFight)
                    .where(
                        LeagueFight.time_to_start == datetime.now(),
                        or_(
                            LeagueFight.first_club_id == club_id,
                            LeagueFight.second_club_id == club_id
                        )
                    )
                )
                result = await session.execute(stmt)
                return result.unique().scalars().all()
            
    @classmethod
    async def get_league_matches_last_month(cls) -> list[LeagueFight]:
        async for session in get_session():
            async with session.begin():
                try:
                    league_fights = await session.execute(
                        select(LeagueFight)
                        .where(
                            LeagueFight.time_to_start >= cls.start_day_last_month,
                            LeagueFight.time_to_start < cls.end_day_last_month,
                        )
                        .order_by(LeagueFight.time_to_start.asc())
                    )
                    return league_fights.scalars().all()
                except Exception as e:
                    print(f"Ошибка при получении матчей для команды за прошлый месяц")
        return None

    @classmethod
    async def get_latest_fights_from_current_month(cls) -> list[LeagueFight]:
        async for session in get_session():
            async with session.begin():
                try:
                    subquery = (
                        select(
                            LeagueFight.id,
                            over(
                                func.row_number(), 
                                partition_by=LeagueFight.group_id,
                                order_by=desc(LeagueFight.time_to_start)
                            ).label("rank")
                        )
                        .where(
                            LeagueFight.time_to_start >= cls.first_day_month,
                            LeagueFight.time_to_start < cls.start_next_month
                        )
                        .subquery()
                    )

                    stmt = (
                        select(LeagueFight)
                        .join(subquery, LeagueFight.id == subquery.c.id)
                        .where(subquery.c.rank == 1) 
                    )
                    result = await session.execute(stmt)
                    return result.unique().scalars().all()
                except Exception as e:
                    print(f"Ошибка при получении group_id для команды за текущий месяц: {e}")
                    return None
    
    @classmethod
    async def create_league_fight(
        cls, 
        match_id: int, 
        first_club_id: int, 
        second_club_id: int, 
        time_to_start: datetime,
        group_id: int,
        type_league: TypeLeague,
    ) -> LeagueFight:
        
        league_fight = LeagueFight(
            match_id=match_id,
            first_club_id=first_club_id,
            second_club_id=second_club_id,
            time_to_start=time_to_start,
            group_id=group_id,
            type_league=type_league
        )
        
        async for session in get_session():
            async with session.begin():
                try:
                    session.add(league_fight)
                    merged_obj = await session.merge(league_fight)
                    await session.commit()
                    return merged_obj
                except Exception as e:
                    # await session.rollback()
                    print(f"Ошибка при создании битвы: {e}")
                    return None
                
    @classmethod
    async def get_group_ids_by_league(
        cls,
        type_league: TypeLeague
    ) -> list[int]:
        async for session in get_session():
            async with session.begin():
                stmt = (
                    select(LeagueFight.group_id)
                    .where(
                        LeagueFight.type_league == type_league,
                        LeagueFight.time_to_start >= cls.first_day_month,
                        LeagueFight.time_to_start < cls.start_next_month
                    )
                    .distinct()
                )
                result = await session.execute(stmt)
                return result.unique().scalars().all()
    