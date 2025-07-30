from database.models.character import Character
from database.models.reminder_character import ReminderCharacter
from database.models.item import Item

from database.session import get_session
from sqlalchemy import select, update, or_
from config import CONST_ENERGY, CONST_VIP_ENERGY
from datetime import datetime, timedelta
from enum import Enum

from constants import PositionCharacter

from logging_config import logger


class CharacterService:
    @classmethod
    async def get_all_characters(cls) -> list[Character]:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(Character)
                )
                all_characters_not_bot = result.unique().scalars().all()
                return all_characters_not_bot
   


    @classmethod
    async def get_all_users_not_bot(cls) -> list[Character]:
        two_months_ago = datetime.now() - timedelta(days=60)
        async for session in get_session():
            async with session.begin():
                stmt = (
                    select(Character)
                    .where(Character.is_bot == False)
                    .join(ReminderCharacter)
                    .where(
                        or_(
                            ReminderCharacter.education_reward_date >= two_months_ago,
                            ReminderCharacter.time_to_join_club >= two_months_ago
                        )
                    )
                )
                result = await session.execute(stmt)
                all_characters_not_bot = result.unique().scalars().all()
                return all_characters_not_bot
   
    @classmethod
    async def get_character(cls, character_user_id: int) -> Character:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(Character).where(Character.characters_user_id == character_user_id)
                )
                current_character = result.scalar_one_or_none()
                return current_character
            

    @classmethod
    async def get_character_by_id(cls, character_id: int) -> Character:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(Character).where(Character.id == character_id)
                )
                current_character = result.scalar_one_or_none()
                return current_character
    
            
    
    @classmethod
    async def create_character(cls, character_obj: Character) -> Character:
        character_obj.gender = character_obj.gender.value
        character_obj.position = character_obj.position.value
        
        async for session in get_session():
            async with session.begin():
                try:
                    session.add(character_obj)
                except:
                    pass
                merged_obj = await session.merge(character_obj)
                await session.commit()
                return merged_obj
            
    @classmethod
    async def update_character_characteristic(cls, character_id: int, type_characteristic: str, amount_add_points: int) -> Character:
        async for session in get_session():
            async with session as sess:
                try:
                    stmt = (
                        update(Character)
                        .where(Character.id == character_id)
                        .values({type_characteristic: getattr(Character, type_characteristic) + amount_add_points})
                    )
                    await sess.execute(stmt)
                    await sess.commit()
                except Exception as E:
                    logger.error(
                        f"Ошибка при изменении характеристики у персонажа с ID {character_id}. "
                        f"Характеристика: '{type_characteristic}', добавленные очки: {amount_add_points}. "
                        f"Текст ошибки: {E}"
                    )
            

    @classmethod
    async def update_training_params(cls, character_obj: Character, characteristic: str, training_time: datetime) -> Character:
        async for session in get_session():
            async with session.begin():
                try:
                    session.add(character_obj)
                except:
                    pass
                merged_obj = await session.merge(character_obj)
                setattr(merged_obj, 'training_characteristic', characteristic)
                setattr(merged_obj, 'time_character_training', training_time)
                await session.commit()
                return merged_obj


    @classmethod
    async def consume_energy(cls, character_id: int, energy_consumed: int) -> Character:
        async for session in get_session():
            async with session.begin():
                character = await session.get(Character, character_id)
                if character:
                    character.current_energy -= energy_consumed
                    await session.flush()

                
    
    @classmethod
    async def edit_character_energy(
        cls, 
        character_id: int, 
        amount_energy: int) -> Character:
        async for session in get_session():
            async with session.begin():
                character = await session.get(Character, character_id)
                if character:
                    character.current_energy += amount_energy
                    await session.flush()
                
    @classmethod        
    async def update_character_club_id(cls,character: Character ,club_id: int):
        async for session in get_session():
            async with session.begin():
                try:
                    session.add(character)
                except:
                    pass
                character.club_id = club_id
                if not character.is_bot:
                    character.reminder.time_to_join_club = datetime.now()
                merged_obj = await session.merge(character)
                await session.commit()
                return merged_obj
            
    @classmethod
    async def update_energy_for_non_bots(cls):
        async for session in get_session():
            async with session.begin():
                try:
                    stmt = (
                        update(Character)
                        .where(Character.is_bot == False)
                        .where(Character.current_energy <= CONST_ENERGY)
                        .values(current_energy=CONST_ENERGY)
                    )
                    stmt_vip = (
                        update(Character)
                        .where(Character.is_bot == False)
                        .where(Character.vip_pass_expiration_date > datetime.now())
                        .where(Character.current_energy <= CONST_VIP_ENERGY)
                        .values(current_energy=CONST_VIP_ENERGY)
                    )
                    await session.execute(stmt)
                    await session.execute(stmt_vip)
                    await session.commit()
                except Exception as e:
                    raise e
                
    @classmethod
    async def get_character_how_update_energy(cls) -> list[Character]:
        async for session in get_session():
            async with session.begin():
                try:
                    result = await session.execute(
                        select(Character)
                        .where(Character.is_bot == False)
                        .where(Character.current_energy <= CONST_ENERGY) 
                        .where(Character.vip_pass_expiration_date <= datetime.now())
                    )
                    all_characters_not_bot = result.unique().scalars().all()
                    return all_characters_not_bot
                except Exception as e:
                    raise e
                
                
    @classmethod
    async def leave_club(cls, character: Character):
        async for session in get_session():
            async with session.begin():
                try:
                    character.club_id = None
                    session.add(character)
                    merged_obj = await session.merge(character)
                    await session.commit()
                    return merged_obj
                except Exception as e:
                    await session.rollback()
                    raise e
                
    @classmethod
    async def update_money_character(cls, character_id: int, amount_money_adjustment: int):
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Character)
                    .where(Character.id == character_id) 
                    .values(money=Character.money + amount_money_adjustment) 
                )
                await session.execute(stmt)
                await session.commit()
                
    @classmethod
    async def add_exp_character(cls, character_id: int, amount_exp_add: int):
        async for session in get_session():
            async with session.begin():
                stmt_select = select(Character).where(Character.id == character_id)
                result = await session.execute(stmt_select)
                character = result.scalar_one()

                character.exp += amount_exp_add

                session.add(character)
                await session.commit()
                
                
    @classmethod
    async def update_character_education_time(cls, character: Character, amount_add_time: timedelta):
        async for session in get_session():
            async with session.begin():
                try:
                    session.add(character)
                except:
                    pass
                character.reminder.education_reward_date = datetime.now()+amount_add_time
                merged_obj = await session.merge(character)
                await session.commit()
                return merged_obj
            
                
    @classmethod
    async def equip_item(cls, character_obj: Character, item_obj: Item) -> Character:
        category_field_map = {
            'T_SHIRT': 't_shirt_id',
            'SHORTS': 'shorts_id',
            'GAITERS': 'gaiters_id',
            'BOOTS': 'boots_id'
        }
        item_category = item_obj.category.value.upper() if isinstance(item_obj.category, Enum) else item_obj.category.upper()
        field_name = category_field_map.get(item_category)

        async for session in get_session():
            async with session.begin():
                try:
                    session.add(character_obj)
                except:
                    pass
                
                merged_character = await session.merge(character_obj)
                setattr(merged_character, field_name, item_obj.id)
                await session.commit()
                
                return merged_character
            

    @classmethod
    async def edit_status_reward_by_referal(cls, character_user_id: int):
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Character)
                    .where(Character.characters_user_id == character_user_id)
                    .values(referral_award_is_received=True)
                )
                await session.execute(stmt)
                await session.commit()
                
    @classmethod
    async def get_my_referals(cls, character_user_id: int):
        async for session in get_session():
            async with session.begin():
                try:
                    result = await session.execute(
                        select(Character)
                        .where(Character.referal_user_id == character_user_id))
                    all_characters_not_bot = result.unique().scalars().all()
                    return all_characters_not_bot
                except Exception as e:
                    raise e
                


                
    @classmethod
    async def change_position(
        cls,
        character_id: Character,
        position: str
    ):
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Character)
                    .where(Character.id == character_id)
                    .values(position=position)
                )
                await session.execute(stmt)
                await session.commit()                
                
    @classmethod
    async def add_trainin_key(
        cls,
        character_id: int,
    ):
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Character)
                    .where(Character.id == character_id)
                    .values(training_key= Character.training_key + 1)
                )
                await session.execute(stmt)
                await session.commit()
                
    @classmethod
    async def remove_training_key(
        cls,
        character_id: int,
    ):
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Character)
                    .where(Character.id == character_id)
                    .values(training_key= Character.training_key - 1)
                )
                await session.execute(stmt)
                await session.commit()
                
    @classmethod
    async def get_characters_by_position(
        cls,
        position: PositionCharacter
    ) -> list[Character]:
        
        async for session in get_session():
            async with session.begin():
                
                stmt = (
                    select(Character)
                    .where(Character.position == position.value)
                    .where(Character.is_bot == False)
                )
                
                result = await session.execute(stmt)
                characters = result.unique().scalars().all()
                return characters
            
    @classmethod
    async def update_get_new_member_bonus(
        cls,
        character_id: int,
    ):
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Character)
                    .where(Character.id == character_id)
                    .values(time_get_member_bonus=datetime.now())
                )
                await session.execute(stmt)
                await session.commit()