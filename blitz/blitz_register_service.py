from sqlalchemy import select
from sqlalchemy.orm import selectinload

from blitz.exception import BlitzCloseError, CharacterExistsInBlitzError
from database.models.blitz import Blitz
from database.models.blitz_character import BlitzCharacter
from database.models.character import Character
from database.session import get_session


class BlitzRegisterService:

    @classmethod
    async def add_character_to_blitz(cls, blitz_id: int, character: Character) -> BlitzCharacter:

        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(Blitz).where(Blitz.id == blitz_id)
                )
                blitz: Blitz = result.scalar_one_or_none()
                if not blitz:
                    raise ValueError(f"Blitz with id {blitz_id} does not exist")
                if not blitz.can_register:
                    raise BlitzCloseError(f"Blitz with id {blitz_id} is not registered")
                result = await session.execute(
                    select(BlitzCharacter).where(
                        BlitzCharacter.character_id == character.id,
                        BlitzCharacter.blitz_id == blitz_id
                    )
                )
                existing: BlitzCharacter = result.scalar_one_or_none()
                if existing:
                    print(f"Blitz Character with id {existing.id} already exists!")
                    raise CharacterExistsInBlitzError(f"Blitz Character with id {existing.id} already exists!")
                blitz_character = BlitzCharacter(
                    character_id=character.id,
                    blitz_id=blitz_id
                )
                session.add(blitz_character)
                await session.flush()
                return blitz_character

    @classmethod
    async def get_blitz_by_id(cls, blitz_id: int) -> Blitz:
        async for session in get_session():
            result = await session.execute(select(Blitz).where(Blitz.id == blitz_id))
            return result.scalar_one_or_none()

    @classmethod
    async def get_blitz_character(cls, blitz_id: int) -> list[BlitzCharacter]:
        blitz: Blitz = await cls.get_blitz_by_id(blitz_id)
        return blitz.characters

    @classmethod
    async def get_characters_from_blitz_character(cls, blitz_id: int) -> list[Character]:
        blitz_characters: list[BlitzCharacter] = await cls.get_blitz_character(blitz_id)
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
