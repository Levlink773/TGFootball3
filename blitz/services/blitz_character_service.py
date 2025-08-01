from sqlalchemy import select

from database.models.blitz_character import BlitzCharacter
from database.models.character import Character
from database.session import get_session


class BlitzCharacterService:
    @classmethod
    async def get_character_from_blitz_character(cls, blitz_character: BlitzCharacter) -> Character | None:
        async for session in get_session():
            result = await session.execute(
                select(Character)
                .where(Character.id == blitz_character.character_id)
            )
            return result.scalar_one_or_none()