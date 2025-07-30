from sqlalchemy.future import select
from sqlalchemy import func, update

from database.session import get_session
from database.models.club_infrastructure import ClubInfrastructure

from bot.club_infrastructure.types import NameInfrastructureType, InfrastructureLevel


class ClubInfrastructureService:
    
    @classmethod
    async def create_infrastructure(
        cls,
        club_id: int
    ) -> ClubInfrastructure:
        async for session in get_session():
            club_infrastructure = ClubInfrastructure(
                club_id = club_id
            )
            session.add(club_infrastructure)
            await session.commit()
            await session.refresh(club_infrastructure)
            return club_infrastructure
                
    @classmethod
    async def get_infrastructure(
        cls,
        club_id: int
    ) -> ClubInfrastructure | None:
        async for session in get_session():
            async with session.begin():
                sql = select(ClubInfrastructure).where(ClubInfrastructure.club_id == club_id)
                result = await session.execute(sql)
                return result.scalar_one_or_none()
            
    @classmethod
    async def add_points(
        cls,
        club_id: int,
        points: int
    ) -> None:
        async for session in get_session():
            async with session.begin():
                sql = (
                    update(ClubInfrastructure)
                    .where(ClubInfrastructure.club_id == club_id)
                    .values(points = ClubInfrastructure.points + points)
                )
                await session.execute(sql)
                await session.commit()
            
    @classmethod
    async def update_level_infrastructure(
        cls,
        club_id: int,
        infrastructure_type: NameInfrastructureType,
        infrastructure_level: InfrastructureLevel
    ) -> None:
        async for session in get_session():
            async with session.begin():
                sql = (
                    update(ClubInfrastructure)
                    .where(ClubInfrastructure.club_id == club_id)
                    .values({infrastructure_type: infrastructure_level})
                )
                await session.execute(sql)
                await session.commit()
                
    @classmethod
    async def reduce_points(
        cls,
        club_id: int,
        points: int
    ) -> None:
        async for session in get_session():
            async with session.begin():
                sql = (
                    update(ClubInfrastructure)
                    .where(ClubInfrastructure.club_id == club_id)
                    .values(points = func.greatest(ClubInfrastructure.points - points, 0))
                )
                await session.execute(sql)
                await session.commit()