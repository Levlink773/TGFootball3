from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

from training.constans import TIMERS_REGISTER_TRAINING
from training.sender.sender_notification import NotificationSender

from .training_timer import Timer

class StarterTrainingTimers:
    _time_rigster_training = TIMERS_REGISTER_TRAINING
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    async def start_trainings_timers(self) -> None:
        for time_register in self._time_rigster_training:
            await self._start_taimer(time_register)
        self.scheduler.start()
        
    async def _start_taimer(self, time_register: str) -> None: 
        time_register: datetime = self._get_time_prerigster(time_register)   
        timer_training = Timer(time_register)
        self.scheduler.add_job(
            timer_training.start_training,
            trigger=DateTrigger(time_register),
            misfire_grace_time=10
        )
    
    def _get_time_prerigster(self, time_register: str) -> datetime:
        now = datetime.now()
        time_register = datetime.strptime(
            time_register, "%H:%M"
        ).replace(
            year   = now.year, 
            month  = now.month, 
            day    = now.day,
            second = 0
        )
        return time_register

class SchedulerRegisterTraining:
    
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self.notification_sender = NotificationSender()
        self.starter_training_timers = StarterTrainingTimers()
        
    async def _start(self) -> None:
        await self.notification_sender.send_notification() 
        await self.starter_training_timers.start_trainings_timers()
        
    async def start(self) -> None:
        #await self._start()
        self.scheduler.add_job(
            self._start,
            trigger=CronTrigger(hour=8, minute=0)
        )
        self.scheduler.start()
