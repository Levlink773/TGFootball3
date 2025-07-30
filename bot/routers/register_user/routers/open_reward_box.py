import asyncio

from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.models.character import Character
from bot.boxes.base_item import Energy, Money
from bot.boxes.base_open import OpenBox
from bot.boxes.base_box import Box
from services.character_service import CharacterService
from .end_training import RewardManager

NEW_MEMBER_BOX = Box(
    items=[
        Energy(
            min=100,
            max=150
        ),
        Money(
            min=30,
            max=100
        )
    ]
)

open_box_new_member_router = Router()


@open_box_new_member_router.callback_query(
    F.data == "open_box_new_member"
)
async def open_box_new_member_handler(
    query: CallbackQuery,
    character: Character
):
    await query.message.delete()
    manager = RewardManager()
    manager.mark_as_received(character.characters_user_id)
    message = await query.message.answer("...")
    open_box = OpenBox(NEW_MEMBER_BOX.winner_items)
    frame_generator = open_box.get_next_frame()
    for num, frame in enumerate(frame_generator):
        if frame and num % 3 == 0:
            await message.edit_text(text=frame)
        await asyncio.sleep(0.3)

    await query.message.answer(
        text = (
            f"Вітаємо! Ви відкрили 🎁 Кейс Новочка і отримали: "
            f"{open_box.winner_item.description} x {open_box.winner_item.count_item}. "
            "<b>Радіємо разом з вами!</b>"
        )
    )
    
    if open_box.winner_item.description == "Енергія":
        await CharacterService.edit_character_energy(
            character_id  = character.id,
            amount_energy = open_box.winner_item.count_item
        )
    else:
        await CharacterService.update_money_character(
            character_id = character.id,
            amount_money_adjustment = open_box.winner_item.count_item
        )