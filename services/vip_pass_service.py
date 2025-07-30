from datetime import datetime, timedelta

from database.models.character import Character

from sqlalchemy import select, update

from database.session import get_session
from logging_config import logger

class VipPassService:
    
    @classmethod
    async def update_vip_pass_time(
        cls,
        character: Character,
        day_vip_pass: int
    ):
        async for session in get_session():
            async with session.begin():
                current_time = datetime.now()
                
                new_vip_pass_time = current_time + timedelta(days=day_vip_pass)
                   
                if character.vip_pass_expiration_date is not None: 
                    if character.vip_pass_expiration_date > current_time:
                        new_vip_pass_time = character.vip_pass_expiration_date + timedelta(days=day_vip_pass)
                    
                stmt = (
                    update(Character)
                    .where(Character.id == character.id)
                    .values(vip_pass_expiration_date=new_vip_pass_time)
                )
                await session.execute(stmt)
                await session.commit()
    
    
    @classmethod
    async def get_have_vip_pass_characters(cls) -> list[Character]:
        async for session in get_session():
            try:
                stmt = (
                    select(Character)
                    .where(Character.vip_pass_expiration_date >  datetime.now())
                )
                result = await session.execute(stmt)
                return result.unique().scalars().all()
            except Exception as E:
                logger.error(f"Failed to get vip pass characters\nError: {E}")