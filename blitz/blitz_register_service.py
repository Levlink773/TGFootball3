from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models.blitz import Blitz
from database.models.blitz_character import BlitzCharacter
from database.models.character import Character
from database.session import get_session


class BlitzRegisterService:
    current_blitz_id: int = -1
    can_register: bool = True

    @classmethod
    async def add_character_to_blitz(cls, character: Character) -> BlitzCharacter:
        if cls.current_blitz_id == -1:
            raise ValueError("Blitz is not initialized")

        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(Blitz).where(Blitz.id == cls.current_blitz_id)
                )
                blitz = result.scalar_one_or_none()
                if not blitz:
                    raise ValueError(f"Blitz with id {cls.current_blitz_id} does not exist")

                result = await session.execute(
                    select(BlitzCharacter).where(
                        BlitzCharacter.character_id == character.id,
                        BlitzCharacter.blitz_id == cls.current_blitz_id
                    )
                )
                existing: BlitzCharacter = result.scalar_one_or_none()
                if existing:
                    print(f"Blitz Character with id {existing.id} already exists!")
                    return existing

                blitz_character = BlitzCharacter(
                    character_id=character.id,
                    blitz_id=cls.current_blitz_id
                )
                session.add(blitz_character)
                await session.flush()
                return blitz_character

    @classmethod
    async def get_blitz_by_id(cls) -> Blitz:
        async for session in get_session():
            result = await session.execute(select(Blitz).where(Blitz.id == cls.current_blitz_id))
            return result.scalar_one_or_none()
    @classmethod
    async def get_blitz_character(cls) -> list[BlitzCharacter]:
        blitz: Blitz = await cls.get_blitz_by_id()
        return blitz.characters

    @classmethod
    async def get_characters_from_blitz_character(cls) -> list[Character]:
        blitz_characters: list[BlitzCharacter] = await cls.get_blitz_character()
        character_ids = [bc.character_id for bc in blitz_characters]

        if not character_ids:
            return []

        async for session in get_session():
            result = await session.execute(
                select(Character)
                .where(Character.id.in_(character_ids))
                .options(selectinload(Character.owner), selectinload(Character.club))
            )
            characters = result.scalars().all()
            return characters
