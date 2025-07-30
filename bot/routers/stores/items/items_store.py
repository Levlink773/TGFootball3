from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models.character import Character
from database.models.item import Item
from database.models.user_bot import (
    STATUS_USER_REGISTER,
    UserBot
)

from services.character_service import CharacterService
from services.items_service import ItemService
from services.user_service import UserService

from bot.keyboards.magazine_keyboard import (
    menu_stores, 
    gradation_values_item, 
    select_items_for_buy,
    select_type_items_keyboard
    )
from bot.callbacks.magazine_callbacks import SelectTypeItems, SelectGradationLevelItem, ByItems
from bot.routers.register_user.routers.buy_first_equipment import get_reward_buying_item

from utils.item_utils import read_items, text_info_items

from constants import MAGAZINE_PHOTO

import json

items_store_router = Router()

@items_store_router.callback_query(SelectTypeItems.filter())
async def select_item(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: SelectTypeItems
):
    user = await UserService.get_user(
        user_id = query.from_user.id
    )
    new_user = False
    if user.status_register == STATUS_USER_REGISTER.BUY_EQUIPMENT:
        new_user = True
    data_items = await read_items()
    await state.update_data(data_items=data_items)
    
    max_leve_item = max(item["level_required"] for item in data_items)
    
    await query.message.answer(
        "Виберіть градацію рівня", 
        reply_markup=gradation_values_item(
            item_сategory= callback_data.item,
            max_level_item=max_leve_item,
            new_user=new_user
        )
    )
    
@items_store_router.callback_query(SelectGradationLevelItem.filter())
async def select_gradation_level(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: SelectGradationLevelItem,
    user: UserBot
):
    data = await state.get_data()
    if user.status_register == STATUS_USER_REGISTER.BUY_EQUIPMENT:
        filtered_items = [data['data_items'][0]]
    else:
        filtered_items = [
            item for item in data['data_items'] 
            if item["category"] == callback_data.item_category and item["level_required"] == callback_data.min_level_item
        ]
        
    await query.message.answer(text = ("📍 Вибери яку річ яку хочеш купити\n" + text_info_items(filtered_items)) , 
                               reply_markup=select_items_for_buy(filtered_items))

    
    
@items_store_router.callback_query(ByItems.filter())
async def select_gradation_level(query: CallbackQuery, state: FSMContext, character: Character, callback_data: ByItems):
    data = await state.get_data()
    item = [item for item in data["data_items"] if item['id'] == callback_data.id_item][0]
    
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
    user = await UserService.get_user(
        user_id=character.characters_user_id
    )
    if user.status_register == STATUS_USER_REGISTER.BUY_EQUIPMENT:
        await get_reward_buying_item(query, character)