from datetime import time, datetime
from typing import Optional

from sqlalchemy import select

from blitz.blitz_register_service import BlitzRegisterService
from blitz.blitz_reminder import BlitzReminder
from database.models.blitz import Blitz
from database.session import get_session


class StartBlitzs:
    @staticmethod
    async def start(start_times: list[time]):
        StartBlitzs.validate_start_times(start_times)

        while True:
            for start_time in start_times:
                await StartBlitz(start_time).start()

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
    def __init__(self, start_time: time):
        self.start_time = start_time

    async def __register_blitz(self) -> Optional[Blitz]:
        current_datetime = self.__start_time_as_datetime()

        async for session in get_session():
            async with session.begin():
                result = await session.execute(select(Blitz))
                blitz: Blitz = result.scalars().first()

                if not blitz:
                    new_blitz = Blitz(start_at=current_datetime)
                    session.add(new_blitz)
                    await session.flush()
                    return new_blitz

                if blitz.start_at == current_datetime:
                    return blitz

                await session.delete(blitz)
                new_blitz = Blitz(start_at=current_datetime)
                session.add(new_blitz)
                await session.flush()
                return new_blitz

    async def start(self):
        blitz: Blitz = await self.__register_blitz()
        BlitzRegisterService.current_blitz_id = blitz.id

        await BlitzReminder(self.start_time).remind()
        print("🏁 Блиц начинается!")
        BlitzRegisterService.can_register = False


    def __start_time_as_datetime(self) -> datetime:
        now = datetime.now()
        return datetime.combine(now.date(), self.start_time)
