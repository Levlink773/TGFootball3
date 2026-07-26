"""schedule_match_reminders — чистая логика планирования, БД не нужна.

Проверяем главное: сколько джоб реально ставится и что напоминание не встаёт
вплотную к общей рассылке-приглашению (иначе игрок получает два сообщения
в одну секунду — так было бы у ЕвроКубков T-40 и Ліги Новачків T-15).
"""
from datetime import datetime, timedelta

from league.user_sender import REMINDER_MINUTES, schedule_match_reminders


class FakeScheduler:
    def __init__(self):
        self.jobs = []

    def add_job(self, func, trigger=None, kwargs=None, misfire_grace_time=None):
        self.jobs.append(kwargs["minutes_left"])


class FakeSender:
    async def send_reminder(self, minutes_left):
        pass


def _run(start_offset_minutes, blast_offset_minutes=None):
    now = datetime.now()
    start = now + timedelta(minutes=start_offset_minutes)
    blast = start - timedelta(minutes=blast_offset_minutes) if blast_offset_minutes else None
    sched = FakeScheduler()
    count = schedule_match_reminders(sched, FakeSender(), start, blast_at=blast)
    return count, sched.jobs


def test_all_three_tiers_when_blast_is_far():
    # Ліга за замовчуванням: рассылка в T-45, матч через 2 часа.
    count, tiers = _run(120, blast_offset_minutes=45)
    assert count == 3
    assert tiers == list(REMINDER_MINUTES)


def test_skips_tier_colliding_with_blast_at_t40():
    # ЕвроКубки: рассылка ровно в T-40 → тир 40 пропускаем.
    count, tiers = _run(120, blast_offset_minutes=40)
    assert count == 2
    assert 40 not in tiers


def test_skips_tier_colliding_with_blast_at_t15():
    # Ліга Новачків: рассылка в T-15 → тир 15 пропускаем.
    count, tiers = _run(120, blast_offset_minutes=15)
    assert count == 2
    assert 15 not in tiers


def test_nothing_scheduled_for_past_match():
    count, tiers = _run(-60)
    assert count == 0
    assert tiers == []


def test_only_future_tiers_when_match_is_close():
    # До матча 20 минут: T-40 уже в прошлом, остаются 15 и 5.
    count, tiers = _run(20)
    assert count == 2
    assert tiers == [15, 5]
