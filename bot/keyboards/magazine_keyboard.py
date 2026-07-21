from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.user_bot import (
    UserBot,
    STATUS_USER_REGISTER
)

from bot.callbacks.magazine_callbacks import (
    SelectTypeItems, 
    SelectTypeLuxeItems,
    SelectGradationLevelItem,
    SelectLuxeGradationLevelItem,
    ByItems,
    ByLuxeItems,
    SelectBox,
)

from database.models.types import TypeBox
from bot.routers.stores.items.types import TypeItems

ALL_BUTTONS_MENU_STORE = {
    "🎽 Магазин речей": "store_items",
    "🎁 Крамниця лутбоксів": "store_boxes",
    "⚡ Крамниця енергії": "massage_room",
    "💎 Ексклюзивний магазин": "store_luxury",
    "🏦 Банк": "bank",
    "🎫 V.I.P Пасс": "vip_pass",
    "🔄 Зміна позиції": "change_position"
}

AVAILABLE_BUTTONS_BY_STATUS = {
    STATUS_USER_REGISTER.BUY_EQUIPMENT: ['🎽 Магазин речей'],
    STATUS_USER_REGISTER.END_TRAINING: list(ALL_BUTTONS_MENU_STORE.keys())
}


def menu_stores(user: UserBot):
    builder = InlineKeyboardBuilder()
    available_buttons = AVAILABLE_BUTTONS_BY_STATUS.get(user.status_register, [])

    for button_text, callback in ALL_BUTTONS_MENU_STORE.items():
        if button_text in available_buttons:
            if user.status_register != STATUS_USER_REGISTER.END_TRAINING:
                final_text = f"✅ {button_text} ✅"
            else:
                final_text = button_text
            callback_data = callback
        else:
            final_text = f"🔒 {button_text}"
            callback_data = "block"

        builder.button(text=final_text, callback_data=callback_data)

    return builder.adjust(2).as_markup(resize_keyboard=True)


# def menu_stores(user: UserBot):
#     return (InlineKeyboardBuilder()
#             .button(text="🎽 Магазин речей", callback_data="store_items")
#             .button(text="🎁 Крамниця лутбоксів", callback_data="store_boxes")
#             .button(text="⚡ Крамниця енергії", callback_data="massage_room")
#             .button(text="💎 Ексклюзивний магазин", callback_data="store_luxury")
#             .button(text="🏦 Банк", callback_data="bank")
#             .button(text="🎫 V.I.P Пасс", callback_data="vip_pass")
#             .button(text="🔄 Зміна позиції", callback_data="change_position")
#             .adjust(1)
#             .as_markup()
#             )


def select_type_items_keyboard(
    type_item: TypeItems = TypeItems.DEFAULT_ITEM,
    new_user: bool = False    
):  
    callback_data =  SelectTypeItems if type_item == TypeItems.DEFAULT_ITEM else SelectTypeLuxeItems
    block_new_user = "🔒" if new_user else "" 
    builder = InlineKeyboardBuilder()
    builder.button(text = "👕 Футболка", callback_data=callback_data(item="T_SHIRT"))
    builder.button(
        text = f"{block_new_user}🩳 Шорти",
        callback_data=callback_data(item="SHORTS") if not new_user else "block"
    )
    builder.button(
        text = f"{block_new_user}🧦 Гетри",
        callback_data=callback_data(item="GAITERS") if not new_user else "block"
    )
    builder.button(
        text = f"{block_new_user}👢 Бутси",
        callback_data=callback_data(item="BOOTS") if not new_user else "block"
    )
    builder.adjust(1)
    return builder.as_markup()
    
def gradation_values_item(
    item_сategory: str, 
    max_level_item: int,
    type_item: TypeItems = TypeItems.DEFAULT_ITEM,
    new_user: bool = False
):
    keyboard = InlineKeyboardBuilder()
    if new_user:
        max_level_item = 1
    callback_data = SelectGradationLevelItem if type_item == TypeItems.DEFAULT_ITEM else SelectLuxeGradationLevelItem
    for min_level_item in range(1,max_level_item+1):
        keyboard.button(text=f"🔰 з {min_level_item} рівня", 
                        callback_data=callback_data(
                            min_level_item=min_level_item,
                            item_category=item_сategory))
    keyboard.adjust(1)
    return keyboard.as_markup()
    
def select_items_for_buy(
    items: dict,
    type_item: TypeItems = TypeItems.DEFAULT_ITEM
):
    keyboard = InlineKeyboardBuilder()
    callback = ByLuxeItems if type_item == TypeItems.LUXE_ITEM else ByItems
    for item in items:
        keyboard.button(
            text = item['name'], 
            callback_data=callback(
                id_item = item['id']
            )
    )
    return keyboard.adjust(1).as_markup()
    
#===================BOXES
def select_box():
    return (InlineKeyboardBuilder()
            .button(
                text="▪️ Маленький бокс футболіста", 
                callback_data=SelectBox(
                    type_box = TypeBox.SMALL_BOX
                )
            )
            .button(
                text="◾️ Середній бокс футболіста", 
                callback_data=SelectBox(
                    type_box = TypeBox.MEDIUM_BOX
                )
            )
            .button(
                text="◼️ Преміум Бокс",
                callback_data=SelectBox(
                    type_box = TypeBox.LARGE_BOX
                )
            )
            
            .adjust(1)
            .as_markup()
            )

def buy_box(url_payment: str):
    return (InlineKeyboardBuilder()
            .button(
                text = "🎁 Купити бокс", 
                url = url_payment
            )
            .as_markup()
            )
    
