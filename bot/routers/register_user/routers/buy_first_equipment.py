import asyncio
from aiogram.types import  CallbackQuery

from bot.keyboards.menu_keyboard import main_menu
from bot.routers.register_user.config import (
    TEXT_STAGE_REGISTER_USER
)

from database.models.user_bot import STATUS_USER_REGISTER
from database.models.character import Character

from services.user_service import UserService
from services.character_service import CharacterService
from services.items_service import ItemService

from loader import bot

from .new_member_bonus import get_new_member_bonus_handler
from .end_training import RewardManager

async def buy_first_equipment_handler(character: Character) -> None:
    new_status = STATUS_USER_REGISTER.BUY_EQUIPMENT
    await UserService.edit_status_register(
        user_id=character.characters_user_id,
        status=new_status
    )
    user = await UserService.get_user(character.characters_user_id)
    amount_add_money = 30-character.money
    await CharacterService.update_money_character(
        character_id=character.id,
        amount_money_adjustment=amount_add_money
    )
    await bot.send_message(
        chat_id=character.characters_user_id,
        text=TEXT_STAGE_REGISTER_USER[new_status],
        reply_markup=main_menu(user)
    )
    
async def get_reward_buying_item(
    query: CallbackQuery,
    character: Character
) -> None:
    items = await ItemService.get_items_from_character(
        character_id=character.id,
    )
    await CharacterService.equip_item(
        character_obj=character,
        item_obj=items[0]
    )
    await CharacterService.edit_character_energy(
        character_id=character.id,
        amount_energy=50
    )
    await UserService.edit_status_register(
        user_id=character.characters_user_id,
        status=STATUS_USER_REGISTER.END_TRAINING
    )
    user = await UserService.get_user(
        character.characters_user_id
    )
    await bot.send_message(
        chat_id=character.characters_user_id,
        text = TEXT_STAGE_REGISTER_USER[STATUS_USER_REGISTER.END_TRAINING],
        reply_markup=main_menu(user)
    )
    await asyncio.sleep(5)
    await get_new_member_bonus_handler(query, character)
    reward_manager = RewardManager()
    reward_manager.start(character)
