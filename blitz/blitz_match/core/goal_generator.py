import asyncio
import random

from typing import AsyncGenerator
from datetime import datetime, timedelta

from blitz.blitz_match.constans import (
    MAX_EVENTS, 
    MIN_GAP, 
    TIME_EVENT_DONATE_ENERGY
)
from blitz.blitz_match.enum_blitz_match import TypeGoalEvent

class GoalGenerator:
    def __init__(
        self,
        start_time: datetime,
        end_time: datetime,
        count_goals: int,
    ):
        self.start_time = start_time
        self.end_time = end_time
        self.count_goals = count_goals
        self.queue: asyncio.Queue = asyncio.Queue()
        self._producer_task: asyncio.Task | None = None
        self._running = True

    async def start(self) -> None:
        self._producer_task = asyncio.create_task(self._start_producer())


    async def stop(self) -> None:
        self._running = False
        if self._producer_task:
            await self._producer_task


    async def _start_producer(self) -> None:
        events = self.generate_events()
        event_times = self.generate_time_events()

        for event, event_time in zip(events, event_times):
            now = datetime.now()

            if not self._running:
                break

            if event == TypeGoalEvent.GOAL:
                ping_time = event_time - timedelta(seconds=TIME_EVENT_DONATE_ENERGY)
                delay_ping = (ping_time - now).total_seconds()
                if delay_ping > 0:
                    await asyncio.sleep(delay_ping)
                await self.queue.put(TypeGoalEvent.PING_DONATE_ENERGY)

            delay_event = (event_time - datetime.now()).total_seconds()
            if delay_event > 0:
                await asyncio.sleep(delay_event)

            await self.queue.put(event)

        await self.queue.put(None)
        
    async def generate_goals(self) -> AsyncGenerator[TypeGoalEvent, None]:
        while True:
            event = await self.queue.get()
            yield event

    def generate_events(self) -> list[TypeGoalEvent]:
        count_no_goal_event = MAX_EVENTS - self.count_goals
        no_goal_events = [TypeGoalEvent.NO_GOAL for _ in range(count_no_goal_event)]
        goal_events = [TypeGoalEvent.GOAL for _ in range(self.count_goals)]
        all_events = no_goal_events + goal_events
        random.shuffle(all_events)
        return all_events

    def generate_time_events(self) -> list[datetime]:
        safe_start_time = self.start_time + timedelta(seconds=30)
        safe_end_time = self.end_time - timedelta(seconds=30)
        safe_duration = (safe_end_time - safe_start_time).total_seconds()

        total_required_gap = MIN_GAP * (MAX_EVENTS - 1)
        available_time_for_distribution = safe_duration - total_required_gap

        if available_time_for_distribution <= 0:
            raise ValueError("Недостаточно времени с учётом MIN_GAP между событиями.")

        base_interval = available_time_for_distribution / MAX_EVENTS

        event_times = []
        current_time = safe_start_time

        for _ in range(MAX_EVENTS):
            event_times.append(current_time)
            current_time += timedelta(seconds=base_interval + MIN_GAP)

        return event_times