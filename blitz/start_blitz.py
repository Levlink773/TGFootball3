import asyncio
from datetime import datetime, time, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from blitz.blitz_reminder import BlitzReminder
from blitz.blitz_service import BlitzService
from database.models.blitz import Blitz
from database.session import get_session


class StartBlitzs:
    @staticmethod
    async def start(start_times: list[time]):
        StartBlitzs.validate_start_times(start_times)

        while True:
            now = datetime.now()
            next_start_datetime = None

            for t in sorted(start_times):
                potential_start = datetime.combine(now.date(), t)
                if potential_start < now:
                    potential_start += timedelta(days=1)

                if next_start_datetime is None or potential_start < next_start_datetime:
                    next_start_datetime = potential_start
            print(f"Планирую следующий блиц на {next_start_datetime}")
            await StartBlitz(next_start_datetime).start()
            await asyncio.sleep(1)

    @staticmethod
    def validate_start_times(start_times: list[time]):
        minutes = [
            t.hour * 60 + t.minute
            for t in sorted(start_times)
        ]
        for i in range(1, len(minutes)):
            delta = minutes[i] - minutes[i - 1]
            if delta < 60:
                raise ValueError(
                    f"Времена {start_times[i - 1]} и {start_times[i]} находятся ближе чем за 1 час"
                )
        if len(minutes) >= 2:
            wrap_around_delta = (1440 - minutes[-1]) + minutes[0]
            if wrap_around_delta < 60:
                raise ValueError(
                    f"Времена {start_times[-1]} и {start_times[0]} (через полночь) находятся ближе чем за 1 час"
                )


class StartBlitz:
    def __init__(self, start_datetime: datetime):
        self.start_datetime = start_datetime.replace(microsecond=0)

    async def _start_blitz(self) -> Blitz:
        # Здесь будет сама логика блиц турнира
        pass

    async def start(self):
        blitz: Blitz = await BlitzService().get_or_create_blitz_by_start(self.start_datetime)

        await BlitzReminder(blitz, 20, 30).remind()
        print("🏁 Блиц начинается!")
        await self._start_blitz()
        print("🏁 Блиц завершен!")
        await BlitzService.remove_blitz_by_id(blitz.id)
        print("🏁 Блиц удален!")
