from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models.item import Item
from database.models.character import Character

from bot.callbacks.items_callbacks import ViewMyItem, PutOnItem, SellMyItem, UnEquipItem
from bot.callbacks.switcher import SwitchMyItem

from constants import ITEM_PER_PAGE

from .utils_keyboard import pagination_keyboard

emj_item = {
    "BOOTS" : "👞",
    "GAITERS" : "🧦",
    "SHORTS" : "🩳",
    "T_SHIRT" : "👕",
}

def character_keyboard():
    return (InlineKeyboardBuilder()
            .button(text = "📦 Мій інвентар", callback_data="my_inventory")
            .button(text = "🫂 Реферальна система", callback_data="referal_system")
            .adjust(1)
            .as_markup()
            )
    
    
def my_inventory_keyboard(items: list[Item], character: Character, page: int = 0 ):

    start = page * ITEM_PER_PAGE
    end = start + ITEM_PER_PAGE 

    keyboard = InlineKeyboardBuilder()
    keyboard.attach(pagination_keyboard(
        total_items=len(items),
        current_page = page,
        switcher=SwitchMyItem,
        
        ))
    
    for item in items[start:end]:
        text_item = emj_item[item.category] + (" ✅ " if item.id in character.items_ids else " ❌ ") + item.name
        keyboard.button(text = text_item, callback_data=ViewMyItem(item_id=item.id))
        
    keyboard.adjust(3, *[1]*ITEM_PER_PAGE)
    return keyboard.as_markup()


def funtctional_item(item_id: int, character: Character):
    keyboard = InlineKeyboardBuilder()
    if item_id in character.items_ids:
        keyboard.button(text = "📤 Зняти річ", 
                        callback_data= UnEquipItem(item_id=item_id))
    else:
        keyboard.button(text="🏷 Одягнути річ",
                        callback_data= PutOnItem(item_id=item_id))
            
        
    keyboard.button(text = "💳 Продати річ",
                    callback_data=SellMyItem(item_id=item_id))
        
    return keyboard.adjust(1).as_markup()