from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from .add_points_from_league import AddPointsToClub


class ShedulerdistributePoints:
    def __init__(self, time_distribute: datetime, points_manager: AddPointsToClub) -> None:
        self.time_distribute= time_distribute
        self.points_manager = points_manager 
        self.scheduler = AsyncIOScheduler()

    async def start_wait_distribute_points(self):
        trigger = DateTrigger(run_date=self.time_distribute)
        self.scheduler.add_job(
            func=self.points_manager.add_points,
            trigger=trigger,
            misfire_grace_time=20
        )
        self.scheduler.start()
    