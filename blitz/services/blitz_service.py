from typing import Any, Callable, Coroutine

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from blitz.exception import BlitzCloseError, CharacterExistsInBlitzError, MaxUsersInBlitzError
from database.models.blitz import Blitz
from database.models.blitz_character import BlitzCharacter
from database.models.character import Character
from database.session import get_session


class BlitzService:
    @classmethod
    async def get_or_create_blitz_by_start(cls, start_datetime) -> Blitz | None:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(select(Blitz).where(Blitz.start_at == start_datetime))
                blitz: Blitz = result.scalar_one_or_none()

                if not blitz:
                    new_blitz = Blitz(start_at=start_datetime)
                    try:
                       session.add(new_blitz)
                       await session.flush()
                       return new_blitz
                    except IntegrityError:
                        await session.rollback()
                        result = await session.execute(select(Blitz).where(Blitz.start_at == start_datetime))
                        blitz = result.scalar_one()
                        return blitz

                return blitz

    @classmethod
    async def add_character_to_blitz(cls, blitz_id: int, character: Character,
                                     max_character: int) -> BlitzCharacter | None:
        async for session in get_session():
            async with session.begin():
                # Получаем блиц
                result = await session.execute(
                    select(Blitz).where(Blitz.id == blitz_id)
                )
                blitz: Blitz = result.scalar_one_or_none()
                if not blitz:
                    raise ValueError(f"Blitz with id {blitz_id} does not exist")
                if not blitz.can_register:
                    raise BlitzCloseError(f"Blitz with id {blitz_id} is not registered")

                # Проверка — уже есть такой персонаж в блице?
                result = await session.execute(
                    select(BlitzCharacter).where(
                        BlitzCharacter.character_id == character.id,
                        BlitzCharacter.blitz_id == blitz_id
                    )
                )
                existing: BlitzCharacter = result.scalar_one_or_none()
                if existing:
                    raise CharacterExistsInBlitzError(f"Blitz Character with id {existing.id} already exists!")

                # Получаем текущее количество персонажей в блице
                result = await session.execute(
                    select(BlitzCharacter).where(
                        BlitzCharacter.blitz_id == blitz_id
                    )
                )
                current_characters = result.scalars().all()

                if len(current_characters) >= max_character:
                    raise MaxUsersInBlitzError(
                        f"Blitz with id {blitz_id} already has {len(current_characters)} characters. Max is {max_character}.")

                # Добавляем персонажа
                blitz_character = BlitzCharacter(
                    character_id=character.id,
                    blitz_id=blitz_id
                )
                session.add(blitz_character)
                await session.flush()
                return blitz_character

    @classmethod
    async def get_blitz_by_id(cls, blitz_id: int) -> Blitz | None:
        async for session in get_session():
            result = await session.execute(select(Blitz).where(Blitz.id == blitz_id).options(selectinload(Blitz.characters)))
            return result.scalar_one_or_none()

    @classmethod
    async def remove_blitz_by_id(cls, blitz_id: int) -> Any | None:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    delete(Blitz).where(Blitz.id == blitz_id)
                )
                if result.rowcount == 0:
                    raise ValueError(f"Blitz with ID {blitz_id} not found.")
                return result.rowcount

    @classmethod
    async def remove_all_blitzes(cls) -> Callable[[], int] | None:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(delete(Blitz))
                return result.rowcount

    @classmethod
    async def get_blitz_character(cls, blitz_id: int) -> list[BlitzCharacter]:
        blitz: Blitz = await cls.get_blitz_by_id(blitz_id)
        return blitz.characters

    @classmethod
    async def get_characters_from_blitz_character(cls, blitz_id: int) -> None | list[Any] | list[Character]:
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
            return list(characters)
    
