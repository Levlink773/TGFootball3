from database.session import get_session
from sqlalchemy.future import select
from sqlalchemy import func, update

from database.models.christmas_reward import ChristmasReward

from datetime import datetime

class ChristmasRewardService:
    
    @classmethod
    async def create_christmas_reward(
        cls,
        user_id: int
    ) -> ChristmasReward:
        async for session in get_session():
            christmas_reward = ChristmasReward(
                user_id=user_id,
            )
            session.add(christmas_reward)
            await session.commit()
            return christmas_reward
        
    
    @classmethod
    async def get_christmas_reward(
        cls,
        user_id: int
    ) -> ChristmasReward | None:
        async for session in get_session():
            sql = select(ChristmasReward).where(ChristmasReward.user_id == user_id)
            result = await session.execute(sql)
            return result.scalar_one_or_none()
        
    
    @classmethod
    async def update_time_get_reward(
        cls,
        user_id: int
    ) -> None:
        async for session in get_session():
            sql = (
                update(ChristmasReward)
                .where(ChristmasReward.user_id == user_id)
                .values(time_get=datetime.now())
            )
            await session.execute(sql)
            await session.commit()
            
