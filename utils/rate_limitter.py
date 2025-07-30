import asyncio
import time
from aiogram.exceptions import TelegramRetryAfter

from functools import wraps



class RateLimiter:
    rate_limit = 8
    max_parallel_tasks = 3
    last_sent_time = time.time() 
    semaphore = asyncio.Semaphore(max_parallel_tasks) 

    async def wait_for_next(self):
        time_since_last = time.time() - self.last_sent_time
        min_interval = 1 / self.rate_limit

        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last) 
        self.last_sent_time = time.time() 

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await self.wait_for_next()
            async with self.semaphore:
                try:
                    await asyncio.sleep(0.05)
                    return await func(*args, **kwargs)
                except TelegramRetryAfter as e:
                    print(f"Flood wait на {e.retry_after} секунд. Ожидаем...")
                    await asyncio.sleep(e.retry_after)
                    return await wrapper(*args, **kwargs)  
                except Exception as e:
                    print(f"Err: {e}")
        return wrapper
    
rate_limiter = RateLimiter()
