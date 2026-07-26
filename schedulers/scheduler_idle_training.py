"""Напоминание о тренировке: 3ч / 6ч / 24ч простоя, дальше каждые 24ч (Max 26.07).

Заменяет прежний ежедневный пинг в 18:00, у которого НЕ БЫЛО дедупликации вообще:
один и тот же простаивающий игрок получал его каждый день бесконечно.

Почему один почасовой sweep, а не DateTrigger на персонажа:
- хвост «и дальше каждые 24ч» бесконечен, DateTrigger'ы пришлось бы вечно
  перевзводить самим себе;
- планировщик живёт в памяти, рестарт теряет все DateTrigger'ы;
- schedulers/scheduler_vip_pass.py уже показывает, чем это кончается —
  ОТДЕЛЬНЫЙ AsyncIOScheduler на каждого персонажа.
Sweep держит всё состояние в БД, поэтому переживает рестарт by construction.
"""
import random
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from database.session import get_session
from database.models.character import Character
from database.models.reminder_character import ReminderCharacter
from services.character_service import CharacterService
from logging_config import logger
from utils.notify import notify

# Самая дешёвая тренировка (30 хв) стоит 10 энергии — ниже пинговать бессмысленно.
MIN_ENERGY_TO_NUDGE = 10
# Совсем мёртвые аккаунты не трогаем.
DORMANT_AFTER = timedelta(days=30)
# Ранние рубежи; после суток — каждые 24ч.
BOUNDARIES = (timedelta(hours=3), timedelta(hours=6))
DAY = timedelta(hours=24)
# «Йди тренуйся» в 04:00 — это отписка, а не ретеншн.
QUIET_FROM_HOUR = 10
QUIET_TO_HOUR = 22


def due_for(last_at: datetime, now: datetime):
    """Момент самого позднего уже пересечённого рубежа, либо None."""
    elapsed = now - last_at
    if elapsed >= DAY:
        return last_at + (elapsed // DAY) * DAY
    for boundary in reversed(BOUNDARIES):
        if elapsed >= boundary:
            return last_at + boundary
    return None


class IdleText:
    """4 варианта, чтобы не было слепоты на один и тот же текст (Max 26.07)."""
    texts = [
        "🏋️ Твій гравець нудьгує без тренувань!\n\n"
        "Зайди в зал — навіть 30 хвилин дадуть плюс до характеристик. ⚡",
        "⚽ Поки ти відпочиваєш, суперники качаються.\n\n"
        "Час повернутись у тренажерку й наздогнати! 💪",
        "💤 Тренування давно не було.\n\n"
        "Одне заняття — і твій футболіст знову у формі. Погнали! 🔥",
        "🔥 Форма сама не тримається!\n\n"
        "Запусти тренування зараз і зроби крок до статусу легенди. 🏆",
    ]

    @staticmethod
    def get_random_text() -> str:
        return random.choice(IdleText.texts)


class IdleTrainingReminder:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        # ponytail: почасовой проход — рубежи срабатывают в пределах ±1ч от точной
        # отметки, а пересечённые ночью уезжают на 10:05. Upgrade path: */15.
        self.scheduler.add_job(
            func=self.remind_idle,
            trigger=CronTrigger(minute=5),
            misfire_grace_time=600,
        )
        self.scheduler.start()

    async def remind_idle(self):
        now = datetime.now()
        if not (QUIET_FROM_HOUR <= now.hour < QUIET_TO_HOUR):
            return

        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(Character, ReminderCharacter.last_training_at)
                    .join(ReminderCharacter, ReminderCharacter.character_id == Character.id)
                    .where(
                        Character.is_bot == False,
                        Character.is_blocked == False,
                        Character.characters_user_id.isnot(None),
                        Character.current_energy >= MIN_ENERGY_TO_NUDGE,
                        # Тренирующегося сейчас не дёргаем.
                        ReminderCharacter.character_in_training == False,
                        ReminderCharacter.last_training_at.isnot(None),
                        ReminderCharacter.last_training_at >= now - DORMANT_AFTER,
                    )
                )
                rows = result.unique().all()

        # Отправка ВНЕ сессии — как в остальных планировщиках проекта.
        sent = 0
        for character, last_training_at in rows:
            due = due_for(last_training_at, now)
            if due is None:
                continue
            if not await CharacterService.claim_idle_training_reminder(character.id, due):
                continue
            if await notify(
                character,
                IdleText.get_random_text(),
                screen="training",
                button_text="🏋️ Почати тренування",
            ):
                sent += 1
        logger.info(f"Idle training reminder: sent {sent} of {len(rows)} candidates")
