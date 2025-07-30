from database.models.item import Item
from database.models.character import Character


from database.session import get_session
from sqlalchemy import select
from sqlalchemy import delete

from enum import Enum
import json


class ItemService:
    
    @classmethod
    async def create_item(cls, item_obj: Item) -> Item:
        if isinstance(item_obj.category, Enum):
            item_obj.category = item_obj.category.value
        
        async for session in get_session():
            async with session.begin():
                try:
                    session.add(item_obj)
                except:
                    pass
                merged_obj = await session.merge(item_obj)
                await session.commit()
                return merged_obj
            
    @classmethod
    async def get_items_from_character(cls, character_id: int) -> list[Item] | None:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(Item).where(Item.owner_character_id==character_id)
                )
                all_characters_not_bot = result.unique().scalars().all()
                return all_characters_not_bot
   
    @classmethod
    async def get_item(cls, item_id: int) -> Item:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(Item).where(Item.id == item_id)
                )
                return result.scalar_one_or_none()
                
                
    @classmethod
    async def delete_item(cls, item_id: int):
        async for session in get_session():
            async with session.begin():
                await session.execute(
                    delete(Item).where(Item.id == item_id)
                )
                await session.commit()
                
    @classmethod
    async def unequip_item(cls, character_obj: Character, category_item: str):
        name_model_item = {
            "T_SHIRT":"t_shirt_id",
            "SHORTS":"shorts_id",
            "GAITERS":"gaiters_id",
            "BOOTS":"boots_id",
        }
        
        async for session in get_session():
            async with session.begin():
                setattr(character_obj, name_model_item[category_item], None)
                await session.merge(character_obj)
                await session.commit()
