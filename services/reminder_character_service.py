from database.models.reminder_character import ReminderCharacter
from sqlalchemy import select, update

from database.session import get_session
from datetime import datetime

from logging_config import logger

class RemniderCharacterService:
    
    @classmethod
    async def create_character_reminder(cls, character_id: int) -> ReminderCharacter:
        async for session in get_session():
            async with session.begin():
                
                reminder_obj = ReminderCharacter(
                    character_id=character_id
                )
                session.add(reminder_obj)
                merged_obj = await session.merge(reminder_obj)
                await session.commit()
                return merged_obj

    @classmethod
    async def get_characters_in_training(cls) -> list[ReminderCharacter]:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(ReminderCharacter)
                    .where(ReminderCharacter.character_in_training == True)
                )
                characters_in_training = result.unique().scalars().all()
                return characters_in_training
            
    @classmethod
    async def anulate_character_training_status(cls, character_id: int) -> None:
        async for session in get_session():
            async with session.begin():
                try:
                    stmt = (
                        update(ReminderCharacter)
                        .where(ReminderCharacter.character_id == character_id)
                        .values(character_in_training = False)
                    )
                    await session.execute(stmt)
                    await session.commit()
                except Exception as E:
                    logger.error(f"Не смог анулировать статус тренировки для {character_id} err : {E}")
            
    @classmethod
    async def toggle_character_training_status(cls, character_id: int) -> ReminderCharacter:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(select(ReminderCharacter).where(ReminderCharacter.character_id == character_id))
                reminder_character = result.scalars().first()
                if reminder_character:
                    current_status = reminder_character.character_in_training
                    new_status = not current_status
                    reminder_character.character_in_training = new_status

                    await session.commit()
                    return reminder_character
                else:
                    raise ValueError(f"ReminderCharacter не найден для character_id: {character_id}")
                
    @classmethod
    async def update_training_info(cls, 
                        character_id: int,  
                        training_stats: str = None,
                        time_start_training: datetime = None,
                        time_training_seconds: int = None
                                   ):
        async for session in get_session():
            async with session.begin():
                result = await session.execute(select(ReminderCharacter).where(ReminderCharacter.character_id == character_id))
                reminder_character = result.scalars().first()

                reminder_character.training_stats = training_stats
                reminder_character.time_start_training = time_start_training
                reminder_character.time_training_seconds = time_training_seconds

                await session.commit()
                return reminder_character
    
    @classmethod
    async def anulate_training_character(cls, character_id: int) -> None:
        async for session in get_session():
            async with session as sess:
                try:
                    stmt = (update(ReminderCharacter)
                            .where(ReminderCharacter.character_id == character_id)
                            .values(training_stats = None)
                            .values(time_start_training = None)
                            .values(time_training_seconds = None)
                            )
                    await sess.execute(stmt)
                    await sess.commit()
                except Exception as E:
                    logger.error(f"Произошла ошибка при онулирования состояния тренировки {E}")
        
            
    @classmethod
    async def edit_status_duel_character(cls, character_id: int, status: bool):
        async for session in get_session():
            async with session.begin():
                await session.execute(
                    update(ReminderCharacter)
                    .where(ReminderCharacter.character_id == character_id)
                    .values(character_in_duel=status)
                )
                await session.commit()
                
    @classmethod
    async def get_characters_not_training(cls) -> list[ReminderCharacter]:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(ReminderCharacter)
                    .where(ReminderCharacter.character_in_training == False)
                )
                characters_not_training = result.unique().scalars().all()
                return characters_not_training
            
        
    @classmethod
    async def character_in_training(cls, character_id: int) -> bool:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(ReminderCharacter)
                    .where(ReminderCharacter.character_id == character_id)
                )
                character_in_training = result.scalars().first()
                return character_in_training is not None