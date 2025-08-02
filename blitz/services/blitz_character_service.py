from sqlalchemy import select, update

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

    @classmethod
    async def add_goal_to_character(cls, character_id: int):
        async for session in get_session():
            async with session.begin():
                blitz_character = await session.execute(
                    select(BlitzCharacter).where(BlitzCharacter.character_id == character_id)
                )
                blitz_character = blitz_character.scalar_one_or_none()
                blitz_character.goals_count += 1
                await session.commit()

    @classmethod
    async def add_score_to_character(
            cls,
            character_id: int,
            add_score: float
    ) -> None:
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(BlitzCharacter)
                    .where(BlitzCharacter.character_id == character_id)
                    .values(count_score=BlitzCharacter.count_score + add_score)
                )
                await session.execute(stmt)
                await session.commit()