import asyncio
from datetime import datetime, time, timedelta
from typing import Any, Coroutine

from blitz.blitz_reminder import BlitzReminder
from blitz.enum_blitz import BlitzStatus
from blitz.services.blitz_service import BlitzService
from blitz.services.blitz_team_service import BlitzTeamService
from blitz.services.message_sender.blitz_sender import BlitzTeamSender
from database.models.blitz import Blitz


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
    def __init__(self, start_datetime: datetime, stages_of_final: int = 5):
        self.start_datetime = start_datetime.replace(microsecond=0)
        if stages_of_final <= 1:
            raise ValueError("count of final must be greater than 1")
        self.stages_of_final = stages_of_final
        self.necessary_users = 2 ** stages_of_final

    async def _start_blitz(self, blitz_id: int):
        teams = await BlitzTeamService.create_teams(self.necessary_users / 2, blitz_id)
        await BlitzTeamSender.send_teams_message(teams)




    async def start(self) -> BlitzStatus:
        blitz: Blitz = await BlitzService().get_or_create_blitz_by_start(self.start_datetime)

        status = await BlitzReminder(blitz, necessary_count_users=self.necessary_users).remind()
        if not status:
            print("Блиц турнир отменен!")
            return BlitzStatus.CANCELED
        print("🏁 Блиц начинается!")
        await self._start_blitz(blitz.id)
        print("🏁 Блиц завершен!")
        await BlitzService.remove_blitz_by_id(blitz.id)
        print("🏁 Блиц удален!")
        return BlitzStatus.FINISH
