from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.models.character import Character

from services.items_service import ItemService
from services.character_service import CharacterService

from bot.keyboards.character_keyboard import my_inventory_keyboard, funtctional_item
from bot.callbacks.items_callbacks import ViewMyItem, PutOnItem, SellMyItem, UnEquipItem
from bot.callbacks.switcher import SwitchMyItem


from utils.item_utils import view_my_item_text, check_if_item_equipped

from constants import PROCENT_TO_SELL



items_character_router = Router()



@items_character_router.callback_query(F.data == "my_inventory")
async def select_view_my_items(query: CallbackQuery, character: Character):
    my_items = await ItemService.get_items_from_character(character_id=character.id)

    
    if not my_items:
        return await query.answer(text = "У вас немає речей", show_alert=True)
    
    await query.message.answer("Виберіть із ваших предметів", 
                               reply_markup=my_inventory_keyboard(
                                   items=my_items,
                                   character=character,
                                   page=0
                               ))
    
    
@items_character_router.callback_query(ViewMyItem.filter())
async def view_item_handler(query: CallbackQuery, callback_data: ViewMyItem, character: Character):
    
    item = await ItemService.get_item(item_id=callback_data.item_id)
     
    if not item:
        return await query.answer("Цього предмета не існує")
    
    await query.message.answer(
        text=view_my_item_text(item),
        reply_markup=funtctional_item(
            item_id=callback_data.item_id,
            character=character
            )
    )
    
@items_character_router.callback_query(PutOnItem.filter())
async def put_on_item(query: CallbackQuery, character: Character, callback_data: PutOnItem):
    
    item = await ItemService.get_item(item_id=callback_data.item_id)
     
    if not item:
        return await query.answer("Цього предмета не існує")
    
    if not check_if_item_equipped(character, item):
        return await query.answer(text = "У вас уже одягнений цей тип речі", show_alert=True)
    
    await CharacterService.equip_item(
        character_obj=character,
        item_obj=item
    )
    await query.message.answer(f"Ви одягнули: {item.name}")
    
    
@items_character_router.callback_query(SellMyItem.filter())
async def sell_my_item(query: CallbackQuery, character: Character, callback_data: SellMyItem):
    item = await ItemService.get_item(callback_data.item_id)
    if not item:
        return await query.answer("Цього предмета не існує")

    if callback_data.item_id in [character.t_shirt_id, character.boots_id, character.gaiters_id, character.shorts_id]:
        await ItemService.unequip_item(
            character, item.category
        )

    price_for_salle = round(item.price * (PROCENT_TO_SELL / 100))
    await CharacterService.update_money_character(character_id=character.id, amount_money_adjustment=price_for_salle)
    await ItemService.delete_item(callback_data.item_id)
    await query.message.edit_text(f"Ви продали <b>{item.name}</b> за {price_for_salle} монет")
    
    
@items_character_router.callback_query(UnEquipItem.filter())
async def sell_my_item(query: CallbackQuery, character: Character, callback_data: UnEquipItem):
    item = await ItemService.get_item(callback_data.item_id)
    if not item:
        return await query.answer("Цього предмета не існує")
    await ItemService.unequip_item(
            character, item.category
        )

    await query.message.edit_text(f"⚙️ Ви зняли річ - {item.name}")
    
    
@items_character_router.callback_query(SwitchMyItem.filter())
async def switcher_items(query: CallbackQuery, character: Character, callback_data: SwitchMyItem):
    my_items = await ItemService.get_items_from_character(character_id=character.id)
    
    return await query.message.edit_reply_markup(
        reply_markup = my_inventory_keyboard(
                items=my_items,
                character=character,
                page=callback_data.page
                               )
    )