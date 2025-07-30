from datetime import datetime, timedelta

from apscheduler.triggers.date import DateTrigger

from training.core.manager_training import TrainingManager

from training.constans import TIME_TRAINING, TIME_REGISTER_TRAINING

from training.sender.sender_message import RegisterInTrainingSender


from .base_timer import BaseTimer


class Timer(BaseTimer):
    
    _time_training: datetime = TIME_TRAINING
    _time_register_training: timedelta = TIME_REGISTER_TRAINING

    def __init__(self, time_prerigster: datetime) -> None:
        self.time_prerigster = time_prerigster
        super().__init__(
            time_start = time_prerigster + self._time_register_training 
        )
        
        self.sender_message: RegisterInTrainingSender = None
        
    async def start_training(self) -> None:
        await self.send_register_message()
        await self.send_start_message()
        await self.send_end_message()
        self.scheduler.start()
        
    async def send_register_message(self) -> None:
        self.sender_message = RegisterInTrainingSender(
            end_time_register = 
                self.time_prerigster + self._time_register_training
        )
        await self.sender_message.start_send_message()
        
    async def send_start_message(self) -> None:
        self.scheduler.add_job(
            func=TrainingManager.start_training,
            kwargs={
                "range_training_times": [
                    self.time_start, self.time_start + self._time_training
                ]
            },
            trigger=DateTrigger(self.time_start),
            misfire_grace_time=10
        )
        
    async def send_end_message(self) -> None:
        end_time: datetime = (
            self.time_start + self._time_training
        )
        self.scheduler.add_job(
            func=TrainingManager.end_all_trainings,
            trigger=DateTrigger(end_time),
            misfire_grace_time=10
        )