from datetime import datetime, timedelta
from typing import List, Iterable

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, delete, or_
from sqlalchemy.orm import selectinload

from bot.filters.check_admin_filter import CheckUserIsAdmin
from database.models.character import Character
from database.models.reminder_character import ReminderCharacter
from database.models.training import CharacterJoinTraining
from database.models.user_bot import STATUS_USER_REGISTER, UserBot
from database.session import get_session  # скорректируй импорт под свой проект

refresh_router = Router()

def chunked_iterable(it: Iterable[int], size: int = 500):
    """Разбивает список id на чанки по size элементов (чтобы не создавать очень длинных IN-параметров)."""
    it = list(it)
    for i in range(0, len(it), size):
        yield it[i : i + size]
@refresh_router.message(Command("refresh_users_db"), CheckUserIsAdmin())
async def refresh_users_db(message: Message):
    """
    Удаляет персонажей, у которых:
      - владелец (UserBot) имеет статус != END_TRAINING (не завершил тренировку)
      - поле ReminderCharacter.education_reward_date либо NULL, либо старше cutoff (30 дней)
    """
    cutoff = datetime.now() - timedelta(days=45)

    # Используем async context manager для сессии
    async for session in get_session():
        try:
            # SELECT кандидатов (outerjoin — чтобы включать персонажей без ReminderCharacter)
            stmt = (
                select(Character)
                .outerjoin(ReminderCharacter, ReminderCharacter.character_id == Character.id)
                .join(Character.owner)  # join по foreign key characters_user_id -> UserBot
                .where(
                    or_(
                        UserBot.status_register != STATUS_USER_REGISTER.END_TRAINING,
                        ReminderCharacter.education_reward_date.is_(None),
                        ReminderCharacter.education_reward_date < cutoff,
                    )
                )
                .options(
                    selectinload(Character.owner),
                    selectinload(Character.reminder),
                )
                .distinct()
            )

            result = await session.execute(stmt)
            candidates: List[Character] = result.scalars().all()

            if not candidates:
                await message.answer("Кандидатов на удаление не найдено.")
                return

            ids_to_delete = [c.id for c in candidates]
            names_preview = [f"{c.id}:{c.name}" for c in candidates][:50]  # показываем до 50 для превью

            # Отправляем превью (если не нужно, можно убрать)
            await message.answer(
                f"Найдено кандидатов на удаление: {len(ids_to_delete)}.\n"
                f"Превью (до 50): {', '.join(names_preview)}"
            )

            # 1) Удаляем зависимые записи в character_join_training (чанками)
            for chunk in chunked_iterable(ids_to_delete, size=500):
                del_join_stmt = delete(CharacterJoinTraining).where(
                    CharacterJoinTraining.character_id.in_(chunk)
                )
                await session.execute(del_join_stmt)

            # 2) Удаляем связанные reminder_character (если такие есть)
            for chunk in chunked_iterable(ids_to_delete, size=500):
                del_rem_stmt = delete(ReminderCharacter).where(
                    ReminderCharacter.character_id.in_(chunk)
                )
                await session.execute(del_rem_stmt)

            # 3) Удаляем сами персонажи (чанками)
            total_deleted = 0
            for chunk in chunked_iterable(ids_to_delete, size=500):
                del_char_stmt = delete(Character).where(Character.id.in_(chunk))
                res = await session.execute(del_char_stmt)
                # Если нужно, можно попытаться прочитать количество затронутых строк:
                try:
                    total_deleted += res.rowcount or 0
                except Exception:
                    pass

            await session.commit()

            # Сообщаем пользователю итог
            # если rowcount не доступен — показываем ожидаемое количество
            deleted_count = total_deleted or len(ids_to_delete)
            await message.answer(f"Удалено персонажей: {deleted_count}.")
            return

        except Exception as e:
            await session.rollback()
            await message.answer(f"Ошибка при удалении: {e}")
            raise
