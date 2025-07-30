from aiogram.filters.callback_data import CallbackData
from database.models.types import TypeBox

class SelectTypeItems(CallbackData, prefix="select_type_items"):
    item: str

class SelectTypeLuxeItems(CallbackData, prefix="select_type_luxe_items"):
    item: str
    
class SelectGradationLevelItem(CallbackData, prefix = "select_gradation_item"):
    min_level_item: int
    item_category: str

class SelectLuxeGradationLevelItem(CallbackData, prefix = "select_luxe_gradation_item"):
    min_level_item: int
    item_category: str

class ByItems(CallbackData, prefix = "buyItem"):
    id_item: int

class ByLuxeItems(CallbackData, prefix = "buyLuxeItem"):
    id_item: int
    
class SelectBox(CallbackData, prefix = "select_box"):
    type_box: TypeBox
    
class BuyBox(CallbackData, prefix = "buy_box"):
    type_box: TypeBox