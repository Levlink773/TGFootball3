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
        # Вызывается и на старте процесса, и по крону в 08:00 — второй start()
        # уронил бы SchedulerAlreadyRunningError.
        if not self.scheduler.running:
            self.scheduler.start()

    async def _start_taimer(self, time_register: str) -> None:
        time_register: datetime = self._get_time_prerigster(time_register)
        # Рестарт в 20:00 не должен пытаться вооружить сессии на 10:00 и 13:00.
        if time_register <= datetime.now():
            return
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
        """Крон 08:00: разослать расписание на день И вооружить таймеры сессий."""
        await self.notification_sender.send_notification()
        await self.starter_training_timers.start_trainings_timers()

    async def start(self) -> None:
        # Раньше здесь стояло `#await self._start()` — из-за этого рестарт в любой
        # момент ПОСЛЕ 08:00 не вооружал ни одной сессии на весь остаток дня, и
        # «тренування з тренером» просто не шли. Вооружаем на старте, но БЕЗ
        # рассылки: broadcast остаётся ровно один раз в сутки, по крону.
        await self.starter_training_timers.start_trainings_timers()
        self.scheduler.add_job(
            self._start,
            trigger=CronTrigger(hour=8, minute=0),
            # Дефолт APScheduler — 1 секунда: рестарт в 08:00:30 ронял джобу.
            misfire_grace_time=3600,
        )
        self.scheduler.start()
