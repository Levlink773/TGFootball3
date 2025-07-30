from database.models.club import Club
from database.models.character import Character

from database.session import get_session
from sqlalchemy.future import select
from sqlalchemy import func, update
from typing import Dict, List
from constants import MAX_LEN_MEMBERS_CLUB

from datetime import datetime

class ClubService:
    
    @classmethod
    async def get_club(cls, club_id: int) -> Club:
        async for session in get_session():
            async with session.begin():
                stmt = select(Club).filter_by(id=club_id)
                result = await session.execute(stmt)
                club = result.scalar_one_or_none()
                return club
            
                
            
    @classmethod
    async def get_club_by_owner_id(cls, owner_id: int) -> Club:
        async for session in get_session():
            async with session.begin():
                stmt = select(Club).filter_by(owner_id=owner_id)
                result = await session.execute(stmt)
                club = result.scalar_one_or_none()
                return club


    @classmethod
    async def get_all_clubs(cls) -> list[Club]:
        async for session in get_session():
            async with session.begin():
                stmt = (
                    select(Club)
                    .where(Club.is_fake_club == False)
                )
                result = await session.execute(stmt)
                clubs = result.unique().scalars().all()
                return clubs
            
    @classmethod
    async def get_all_clubs_to_join(
        cls,
        filter_join_to_req: bool = True
    ) -> list[Club]:
        async for session in get_session():
            async with session.begin():
   
                subquery = (
                    select(
                        Club.id.label('club_id'),
                        func.count().label('characters_count')
                    )
                    .select_from(Club)
                    .join(Club.characters)
                    .group_by(Club.id)
                    .subquery()
                )
                

                stmt = (
                    select(Club)
                    .join(subquery, Club.id == subquery.c.club_id)
                    .where(Club.is_fake_club == False)
                    .where(subquery.c.characters_count < MAX_LEN_MEMBERS_CLUB)
                )
                if not filter_join_to_req:
                    stmt = stmt.where(
                        Club.is_invite_only == False
                    )
                result = await session.execute(stmt)
                clubs = result.unique().scalars().all()
                return clubs
            
    @classmethod
    async def create_club(cls, name_club: str, owner_id: int, fake_club = False, league:str  = "🟢 Ліга новачків") -> Club:
        async for session in get_session():
            async with session.begin(): 
                obj = Club(
                    owner_id  = owner_id,
                    name_club = name_club,
                    is_fake_club = fake_club,
                    league = league
                )
                session.add(obj)
                merged_obj = await session.merge(obj)
                return merged_obj
            
    @classmethod
    async def update_link_to_chat(cls, club: Club, new_link: str) -> None:
        async for session in get_session():
            async with session.begin():
                club.link_to_chat = new_link
                merged_obj = await session.merge(club)
                return merged_obj
            
    @classmethod
    async def get_clubs_by_league(cls, league: str) -> None | list[Club]:
        async for session in get_session(): 
            async with session.begin():
                result = await session.execute(
                    select(Club)
                    .where(Club.league == league)
                    .where(Club.is_fake_club == False)
                    .order_by(Club.league)
                    )
                clubs = result.unique().scalars().all()
                return sorted(clubs, key=lambda club: club.total_power, reverse=True)    
            
    @classmethod
    async def donate_energy(cls, club: Club, count_energy: int) -> None:
        async for session in get_session():
            async with session.begin():
                club.energy_applied += count_energy
                merged_obj = await session.merge(club)
                return merged_obj
            
    @classmethod
    async def reset_energy_aplied_not_bot_clubs(cls):
        async for session in get_session():
            async with session.begin():
                await session.execute(
                    update(Club)
                    .where(Club.is_fake_club == False)
                    .values(energy_applied=0)
                )
                await session.commit()
                
    @classmethod
    async def transfer_club_owner(cls, club: Club, new_owner_id: int) -> None:
        async for session in get_session():
            async with session.begin():
                club.owner_id = new_owner_id
                merged_obj = await session.merge(club)
                await session.commit()
                return merged_obj
            
    @classmethod
    async def remove_all_characters_from_club(cls, club: Club) -> None:
        async for session in get_session():
            async with session.begin():
                await session.execute(
                    update(Character)
                    .where(Character.club_id == club.id)
                    .values(club_id=None)
                )
                await session.commit()
                
    @classmethod
    async def remove_character_from_club(cls, character_id: int):
        async for session in get_session():
            async with session.begin():
                try:
                    stmt = (
                        update(Character)
                        .where(Character.id == character_id)
                        .where()
                        .values(club_id = None)    
                            )
                    await session.execute(stmt)
                    await session.commit()
                except Exception as E:
                    print(E)
    
    @classmethod   
    async def edit_schemas(cls, club: Club, new_schema: str):
        async for session in get_session():
            async with session.begin():
                await session.execute(
                    update(Club)
                    .where(Club.id == club.id)
                    .values(schema = new_schema)
                    .values(time_edit_schema = datetime.now())
                )
                await session.commit()
            
    @classmethod
    async def change_name_stadion(cls, club_id: int, new_name_stadion: str) -> None:
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Club)
                    .where(Club.id == club_id)
                    .values(custom_name_stadion=new_name_stadion)
                )
                await session.execute(stmt)
                await session.commit()
                
    @classmethod
    async def change_photo_url_stadion(cls, club_id: int, photo_url: str) -> None:
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Club)
                    .where(Club.id == club_id)
                    .values(custom_url_photo_stadion = photo_url)
                )
                await session.execute(stmt)
                await session.commit()
                
    @classmethod
    async def get_clubs_by_ids(cls, club_ids: list[int]) -> list[Club]:
        async for session in get_session():
            async with session.begin():
                stmt = (
                    select(Club)
                    .where(Club.id.in_(club_ids))
                )
                result = await session.execute(stmt)
                return result.unique().scalars().all()
            
    @classmethod
    async def update_rang_league(
        cls, 
        club_id: int,
        new_rang_league: str
    ):
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Club)
                    .where(Club.id == club_id)
                    .values(league = new_rang_league)
                )
                await session.execute(stmt)
                await session.commit()  
                
    @classmethod
    async def update_description_club(
        cls, 
        club_id: int,
        new_description: str
    ):
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Club)
                    .where(Club.id == club_id)
                    .values(description = new_description)
                )
                await session.execute(stmt)
                await session.commit()
                
                
    @classmethod
    async def change_status_invoice_invite(
        cls,
        club_id: int,
        status: bool
    ) -> None:
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Club)
                    .where(Club.id == club_id)
                    .values(is_invite_only = status)
                )
                await session.execute(stmt)
                await session.commit()