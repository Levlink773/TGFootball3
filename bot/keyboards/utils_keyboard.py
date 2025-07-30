from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.callbacks.switcher import Switcher

ITEM_PER_PAGE = 9

def pagination_keyboard(current_page: int, total_items: int, switcher: Switcher):
    total_pages = (total_items + ITEM_PER_PAGE - 1) // ITEM_PER_PAGE 
    
    def arrow_button(statement: bool, new_page: int, side: str):
        if statement:    
            return InlineKeyboardBuilder().button(
                text="➡️" if side == "right" else "⬅️", 
                callback_data=switcher(
                    page = new_page,
                    side = side
                )
            )
        return InlineKeyboardBuilder().button(text="🟥", callback_data="ignore")
    
    keyboard = InlineKeyboardBuilder()
    keyboard.attach(arrow_button(
                statement = (current_page>0), 
                new_page  = (current_page-1),
                side      = "left"
                                 ))
    
    keyboard.button(text=f"{current_page + 1}/{total_pages}", callback_data="ignore")
    
    keyboard.attach(arrow_button(
                statement = (current_page < total_pages-1), 
                new_page  = (current_page+1),
                side      = "right"
                                 ))
    return keyboard
def menu_plosha():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text = "⬅️ Головна площа")
    keyboard.adjust(1)
    return keyboard