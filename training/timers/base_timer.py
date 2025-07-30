from abc import ABC, abstractmethod
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler


class BaseTimer(ABC):
    
    TIME_START: str
    
    def __init__(self, time_start: datetime) -> None:
        self.scheduler = AsyncIOScheduler()
        self.time_start = time_start
    
    @abstractmethod
    async def start_training(self):
        pass
    