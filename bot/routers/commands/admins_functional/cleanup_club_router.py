from typing import List, Iterable

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, delete, or_, update
from sqlalchemy.orm import selectinload

from bot.filters.check_admin_filter import CheckUserIsAdmin
from database.models.club import Club
from database.models.character import Character
from database.models.club_infrastructure import ClubInfrastructure
from database.models.duel import Duel
from database.models.league_fight import LeagueFight
from database.models.training import CharacterJoinTraining
from database.session import get_session  # поправь импорт под свой проект

club_router = Router()


def chunked_iterable(it: Iterable[int], size: int = 500):
    """Разбивает список id на чанки по size элементов (для безопасных IN-запросов)."""
    it = list(it)
    for i in range(0, len(it), size):
        yield it[i : i + size]


@club_router.message(Command("show_top_clubs"), CheckUserIsAdmin())
async def show_top_clubs(message: Message):
    """
    Показывает топ-80 клубов по силе (total_power) и остальных отдельно.
    """
    async for session in get_session():
        stmt = (
            select(Club)
            .options(selectinload(Club.characters))
        )
        result = await session.execute(stmt)
        all_clubs: List[Club] = result.scalars().all()
        all_clubs = sorted(all_clubs, key=lambda club: club.total_power, reverse=True)

        if not all_clubs:
            await message.answer("Клубов не найдено.")
            return

        top_80 = all_clubs[:80]
        others = all_clubs[80:]

        preview_top = [f"{c.id}:{c.name_club}({c.total_power})" for c in top_80[:20]]
        preview_others = [f"{c.id}:{c.name_club}({c.total_power})" for c in others[:20]]

        msg = (
            f"Всего клубов: {len(all_clubs)}\n"
            f"Топ-80 клубов:\n{', '.join(preview_top)}\n\n"
            f"Остальные (пример):\n{', '.join(preview_others)}"
        )
        await message.answer(msg)


@club_router.message(Command("cleanup_clubs"), CheckUserIsAdmin())
async def cleanup_clubs(message: Message):
    """
    Удаляет клубы (кроме топ-80), у которых:
    - 0 или 1 персонаж, или
    - общая сила меньше 1580.

    Персонажи отсоединяются (club_id = NULL).
    Чистятся связанные дуэли, тренировки, инфраструктура и матчи лиги.
    """
    async for session in get_session():
        try:
            stmt = select(Club).options(selectinload(Club.characters))
            result = await session.execute(stmt)
            all_clubs: List[Club] = result.scalars().all()

            if not all_clubs:
                await message.answer("Клубов не найдено.")
                return

            # сортировка клубов по силе
            all_clubs_sorted = sorted(all_clubs, key=lambda club: club.total_power, reverse=True)
            top_ids = [c.id for c in all_clubs_sorted[:80]]

            # фильтруем клубы на удаление
            to_delete_clubs = [
                c for c in all_clubs_sorted[80:]  # не трогаем топ-80
                if len(c.characters) <= 1 or c.total_power < 1580
            ]
            to_delete_ids = [c.id for c in to_delete_clubs]

            if not to_delete_ids:
                await message.answer("Нет клубов для удаления (≤1 игрок или сила < 1580).")
                return

            # собираем id персонажей
            to_unlink_character_ids = [char.id for c in to_delete_clubs for char in c.characters]

            if to_unlink_character_ids:
                # удаляем дуэли
                for chunk in chunked_iterable(to_unlink_character_ids, size=500):
                    del_duels = delete(Duel).where(
                        or_(Duel.user_1_id.in_(chunk), Duel.user_2_id.in_(chunk))
                    )
                    await session.execute(del_duels)

                # удаляем связи с тренировками
                for chunk in chunked_iterable(to_unlink_character_ids, size=500):
                    del_trainings = delete(CharacterJoinTraining).where(
                        CharacterJoinTraining.character_id.in_(chunk)
                    )
                    await session.execute(del_trainings)

                # отсоединяем персонажей
                for chunk in chunked_iterable(to_unlink_character_ids, size=500):
                    upd_chars = update(Character).where(Character.id.in_(chunk)).values(club_id=None)
                    await session.execute(upd_chars)

            # чистим инфраструктуру
            for chunk in chunked_iterable(to_delete_ids, size=500):
                del_infra = delete(ClubInfrastructure).where(ClubInfrastructure.club_id.in_(chunk))
                await session.execute(del_infra)

            # чистим матчи лиги
            for chunk in chunked_iterable(to_delete_ids, size=500):
                del_fights = delete(LeagueFight).where(
                    or_(
                        LeagueFight.first_club_id.in_(chunk),
                        LeagueFight.second_club_id.in_(chunk)
                    )
                )
                await session.execute(del_fights)

            # удаляем клубы
            total_deleted = 0
            for chunk in chunked_iterable(to_delete_ids, size=500):
                del_clubs = delete(Club).where(Club.id.in_(chunk))
                res = await session.execute(del_clubs)
                try:
                    total_deleted += res.rowcount or 0
                except Exception:
                    pass

            await session.commit()
            await message.answer(f"Удалено клубов: {total_deleted}, персонажи отсоединены.")

        except Exception as e:
            await session.rollback()
            await message.answer(f"Ошибка при удалении: {e}")
            raise
