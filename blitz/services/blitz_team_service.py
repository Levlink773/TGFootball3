import random

from sqlalchemy import select, func
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
            raise ValueError(f"Число команд ({team_count}) должно быть степенью двойки (2, 4, 8, 16, ...).")

        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(BlitzCharacter)
                    .where(BlitzCharacter.blitz_id == blitz_id)
                    .options()  # при необходимости можно добавить selectinload(...)
                )
                characters = list(result.scalars().all())

                expected_players = team_count * 2
                if len(characters) != expected_players:
                    raise ValueError(
                        f"В блице должно быть ровно {expected_players} персонажей, но найдено {len(characters)}."
                    )

                random.shuffle(characters)

                created_teams: list[BlitzTeam] = []

                for i in range(team_count):
                    team = BlitzTeam()
                    session.add(team)
                    await session.flush()

                    char1 = characters[i * 2]
                    char2 = characters[i * 2 + 1]

                    char1.team_id = team.id
                    char2.team_id = team.id

                    created_teams.append(team)

                # Чтобы получить в ответе команды уже с загруженными персонажами:
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
                result = await session.execute(select(BlitzTeam).where(BlitzTeam.id == team_id))
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
