import random
from typing import Callable, Any, Coroutine

from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from database.models.blitz_character import BlitzCharacter
from database.models.blitz_team import BlitzTeam
from database.models.character import Character
from database.session import get_session


class BlitzTeamService:
    @staticmethod
    def is_power_of_two(n: int) -> bool:
        return n > 0 and (n & (n - 1)) == 0

    @classmethod
    async def create_teams(cls, team_count: int, blitz_id: int) -> list[BlitzTeam] | None:
        if not cls.is_power_of_two(team_count):
            raise ValueError(f"Число команд ({team_count}) повинно бути степенем двійки.")

        async for session in get_session():
            async with session.begin():
                stmt = (
                    select(BlitzCharacter, Character)
                    .join(Character, Character.id == BlitzCharacter.character_id)
                    .where(BlitzCharacter.blitz_id == blitz_id)
                )
                result = await session.execute(stmt)
                rows = list(result.all())

                expected = team_count * 2
                if len(rows) != expected:
                    raise ValueError(
                        f"Очікується {expected} учасників, але знайдено {len(rows)}."
                    )

                # 2) Перемішуємо
                random.shuffle(rows)

                created_teams: list[BlitzTeam] = []
                for idx in range(team_count):
                    # беремо по два рядки
                    bc1, char1 = rows[2 * idx]
                    bc2, char2 = rows[2 * idx + 1]

                    # формуємо ім'я команди з імен персонажів
                    team_name = f'Команда {idx + 1} ("{char1.name}", "{char2.name})"'
                    team = BlitzTeam(name=team_name)
                    session.add(team)
                    await session.flush()  # щоб зʼявився team.id

                    # призначаємо цих двох в нову команду
                    bc1.team_id = team.id
                    bc2.team_id = team.id
                    created_teams.append(team)

                # 3) Підтягуємо в teams поле characters
                for team in created_teams:
                    await session.refresh(team, attribute_names=["characters"])

                return created_teams

    @classmethod
    async def get_characters_from_blitz_team(cls, team: BlitzTeam) -> tuple[Character, Character]:
        async for session in get_session():
            result = await session.execute(
                select(Character)
                .join(BlitzCharacter, BlitzCharacter.character_id == Character.id)
                .where(BlitzCharacter.team_id == team.id)
                .options(selectinload(Character.owner))  # загружаем пользователя, если нужно
            )
            characters = result.scalars().all()
            if len(characters) != 2:
                raise ValueError(f"Команда должна содержать 2 персонажа, но найдено: {len(characters)}")
            return characters[0], characters[1]

    @classmethod
    async def get_by_id(cls, team_id: int) -> BlitzTeam | None:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(select(BlitzTeam)
                                               .where(BlitzTeam.id == team_id)
                                               .options(selectinload(BlitzTeam.characters)))
                return result.scalar_one_or_none()
    @classmethod
    def pair_teams(cls, teams: list[BlitzTeam]) -> list[tuple[BlitzTeam, BlitzTeam]]:
        if len(teams) % 2 != 0:
            raise ValueError("Количество команд должно быть чётным")
        return [(teams[i], teams[i + 1]) for i in range(0, len(teams), 2)]
    @classmethod
    async def get_score_team(cls, team_id: int) -> float:
        async for session in get_session():
            stmt = select(func.sum(BlitzCharacter.count_score)).where(
                BlitzCharacter.team_id == team_id
            )
            result = await session.execute(stmt)
            total_score = result.scalar()
            return total_score or 0.0  # Если None — вернём 0.0
        return 0.0

    @classmethod
    async def remove_all_blitz_teams(cls) -> Callable[[], int] | None:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(delete(BlitzTeam))
                return result.rowcount  # Количество удалённых записей

