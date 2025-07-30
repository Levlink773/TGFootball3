from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models.character import Character
from database.models.item import Item

from services.character_service import CharacterService
from services.items_service import ItemService

from bot.keyboards.magazine_keyboard import (
    gradation_values_item, 
    select_items_for_buy,
    )
from bot.callbacks.magazine_callbacks import (
    SelectTypeLuxeItems, 
    SelectLuxeGradationLevelItem, 
    ByLuxeItems
)
from utils.item_utils import read_luxe_items, text_info_items
from .types import TypeItems

import json

luxe_items_store_router = Router()

@luxe_items_store_router.callback_query(SelectTypeLuxeItems.filter())
async def select_item(query: CallbackQuery, state: FSMContext, callback_data: SelectTypeLuxeItems):
    
    data_luxe_items = await read_luxe_items()
    await state.update_data(data_luxe_items=data_luxe_items)
    
    max_leve_item = max(item["level_required"] for item in data_luxe_items)
    
    await query.message.answer(
        "Виберіть градацію рівня", 
        reply_markup=gradation_values_item(
            item_сategory= callback_data.item,
            max_level_item=max_leve_item,
            type_item = TypeItems.LUXE_ITEM
        )
    )
    
@luxe_items_store_router.callback_query(SelectLuxeGradationLevelItem.filter())
async def select_gradation_level(query: CallbackQuery, state: FSMContext, callback_data: SelectLuxeGradationLevelItem):
    data = await state.get_data()
    
    filtered_items = [
        item for item in data['data_luxe_items'] 
        if item["category"] == callback_data.item_category and item["level_required"] == callback_data.min_level_item
    ]
    
    await query.message.answer(
        text = ("📍 Вибери яку річ яку хочеш купити\n" + text_info_items(filtered_items)) , 
        reply_markup=select_items_for_buy(
            filtered_items,
            type_item = TypeItems.LUXE_ITEM
            )
    )

    
    
@luxe_items_store_router.callback_query(ByLuxeItems.filter())
async def select_gradation_level(query: CallbackQuery, state: FSMContext, character: Character, callback_data: ByLuxeItems):
    data = await state.get_data()
    item = [item for item in data["data_luxe_items"] if item['id'] == callback_data.id_item][0]
    
    if character.money < item['price']:
        return await query.answer(text = "У вас не вистачає монет на купівлю цієї речі", show_alert=True)
    
    if character.level < item['level_required']:
        return await query.answer(text = "У вас не вистачає рівня, щоб купити цю річ", show_alert=True)
    item_obj = Item(
        name = item['name'],
        category = item['category'],
        level_required = item['level_required'],
        price = item['price'],
        stats = json.dumps(item['stats']),
        owner_character_id = character.id
    )
    await ItemService.create_item(
        item_obj=item_obj
    )
    await CharacterService.update_money_character(
        character_id=character.id,
        amount_money_adjustment= -item_obj.price
    )

    await query.message.answer(f"Вітаю ви купили річ {item_obj.name}")
    