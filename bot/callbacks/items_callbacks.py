from aiogram.filters.callback_data import CallbackData

class ViewMyItem(CallbackData, prefix="view_my_item"):
    item_id: int
    
    
class PutOnItem(CallbackData, prefix="put_on_item"):
    item_id: int
    

class SellMyItem(CallbackData, prefix="sell_my_item"):
    item_id: int
    

class UnEquipItem(CallbackData, prefix="unequip_item"):
    item_id: int