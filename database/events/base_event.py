import asyncio

from abc import ABC, abstractmethod

class BaseEventListener(ABC):
    
    def __init__(self):
        self.queue = asyncio.Queue()
        
    async def start_listener(self):
        asyncio.create_task(self.process_events())

    @abstractmethod
    async def handle_event(self, instance):
        pass

    async def process_events(self):
        while True:
            instance = await self.queue.get()
            await self.handle_event(instance)

    def __call__(self, instance):
        self.queue.put_nowait((instance))