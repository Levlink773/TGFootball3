from asyncio import Lock
from typing import Optional

class UserLock:

    _lock_manager: dict[int, Lock] = {} 

    def __init__(self, user_id: int) -> None:
        self.user_id: int = user_id
        self.lock: Optional[Lock] = None

    @classmethod
    async def _get_lock(cls, user_id: int) -> Lock:
        if user_id not in cls._lock_manager:
            cls._lock_manager[user_id] = Lock()
        return cls._lock_manager[user_id]

    async def __aenter__(self):
        self.lock = await self._get_lock(self.user_id)
        await self.lock.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.lock:
            self.lock.release()