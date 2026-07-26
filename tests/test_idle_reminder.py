"""due_for — чистая функция рубежей 3ч/6ч/24ч, БД не нужна.

Главное свойство: рубежи монотонно растут, поэтому claim по
`idle_notified_at < due` пропускает ровно одно сообщение на рубеж.
"""
from datetime import datetime, timedelta

from schedulers.scheduler_idle_training import DAY, due_for

NOW = datetime(2026, 7, 26, 14, 0, 0)


def _due(hours):
    return due_for(NOW - timedelta(hours=hours), NOW)


def test_nothing_before_three_hours():
    assert _due(0) is None
    assert _due(2.9) is None


def test_three_hour_tier():
    assert _due(3) == NOW - timedelta(hours=3) + timedelta(hours=3)
    assert _due(5.9) == NOW - timedelta(hours=5.9) + timedelta(hours=3)


def test_six_hour_tier_wins_over_three():
    last = NOW - timedelta(hours=7)
    assert due_for(last, NOW) == last + timedelta(hours=6)


def test_first_daily_tier():
    last = NOW - timedelta(hours=25)
    assert due_for(last, NOW) == last + DAY


def test_repeats_every_24h_and_is_monotonic():
    last = NOW - timedelta(hours=73)
    due = due_for(last, NOW)
    assert due == last + 3 * DAY
    # Следующие сутки простоя дают строго больший рубеж — значит claim пройдёт
    # ещё раз, и ровно один раз.
    later = due_for(last, NOW + DAY)
    assert later == last + 4 * DAY
    assert later > due


def test_tier_is_stable_within_the_same_window():
    """Почасовой sweep не должен слать по сообщению каждый час."""
    last = NOW - timedelta(hours=3)
    first = due_for(last, NOW)
    # Через час рубеж тот же -> claim уже потрачен -> второго сообщения нет.
    assert due_for(last, NOW + timedelta(hours=1)) == first
    assert due_for(last, NOW + timedelta(hours=2)) == first
