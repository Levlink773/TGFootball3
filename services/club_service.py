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
   
                # OUTER join + count(Character.id), and both halves are load-bearing.
                # An inner join drops clubs with zero members entirely, so a freshly
                # created club was invisible in the join list until someone else was
                # already in it — and on an empty database every club was invisible.
                # count(*) would then count the all-NULL row an outer join emits and
                # report an empty club as having 1 member; count(Character.id) skips
                # NULLs and returns 0.
                subquery = (
                    select(
                        Club.id.label('club_id'),
                        func.count(Character.id).label('characters_count')
                    )
                    .select_from(Club)
                    .outerjoin(Club.characters)
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
    async def create_club_checked(cls, name_club: str, owner_id: int) -> Club | None:
        # Clash check + insert in one transaction. Returns None if the name is taken.
        # Advisory only: clubs.name_club has no unique index, so a simultaneous
        # create of the same name can still slip through. Adding the index would
        # turn rename_club's soft `return False` into an IntegrityError, so it is a
        # separate change.
        async for session in get_session():
            async with session.begin():
                clash = await session.execute(
                    select(Club.id).where(
                        Club.name_club == name_club,
                        Club.is_fake_club == False,
                    )
                )
                if clash.scalar_one_or_none() is not None:
                    return None
                obj = Club(
                    owner_id=owner_id,
                    name_club=name_club,
                    is_fake_club=False,
                    league="🟢 Ліга новачків",
                )
                session.add(obj)
                await session.flush()
                return obj

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
        # Atomic increment. The old merge() rewrote the whole stale Club row AND
        # never committed, so concurrent donations lost updates.
        async for session in get_session():
            async with session.begin():
                await session.execute(
                    update(Club)
                    .where(Club.id == club.id)
                    .values(energy_applied=Club.energy_applied + count_energy)
                )
                await session.commit()
        club.energy_applied += count_energy
        return club
            
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
        # Targeted single-column UPDATE — merge() of a detached Club rewrote every
        # loaded column (energy_applied, points, ...) from a stale snapshot.
        async for session in get_session():
            async with session.begin():
                await session.execute(
                    update(Club).where(Club.id == club.id).values(owner_id=new_owner_id)
                )
                await session.commit()
        club.owner_id = new_owner_id
        return club
            
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
    async def rename_club(cls, club_id: int, new_name: str) -> bool:
        # Reject a name already taken by another real club, else rename. Returns False on collision.
        async for session in get_session():
            async with session.begin():
                clash = await session.execute(
                    select(Club.id).where(
                        Club.name_club == new_name,
                        Club.id != club_id,
                        Club.is_fake_club == False,
                    )
                )
                if clash.scalar_one_or_none() is not None:
                    return False
                await session.execute(
                    update(Club).where(Club.id == club_id).values(name_club=new_name)
                )
                await session.commit()
                return True
        return False

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