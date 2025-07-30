import asyncio
from datetime import timedelta

from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from database.models.character import Character
from database.models.christmas_reward import ChristmasReward

from bot.filters.check_time_christmas_tree import CheckTimeChristmasTree
from bot.keyboards.get_christmas_reward import get_christmas_reward_keyboard
from bot.utils.user_lock import UserLock

from services.christmas_reward_service import ChristmasRewardService
from services.character_service import CharacterService

from bot.boxes.base_item import Energy, Money
from bot.boxes.base_open import OpenBox
from .box import cristmas_box

from loader import bot

from constants import (
    CHRISTMAS_TREE_PHOTO,
    MIN_ENERGY_CHRISTMAS_REWARD,
    MAX_ENERGY_CHRISTMAS_REWARD,
    MIN_MONEY_CHRISTMAS_REWARD,
    MAX_MONEY_CHRISTMAS_REWARD
)

get_reward_router = Router()



@get_reward_router.message(
    F.text == "🎄 Новорічна ялинка",
    CheckTimeChristmasTree()
)
async def get_reward_christmas_tree(
    message: Message,
    character: Character
):
    christmas_reward = await ChristmasRewardService.get_christmas_reward(
        user_id = character.characters_user_id
    )
    
    texts = {
        True  : (
        "🎄 Новорічна ялинка у грі! 🎅⚽\n\n"
        "Святковий настрій приходить у ваш клуб! "
        "Загляньте до нашої новорічної ялинки та отримуйте щоденні подарунки:\n"
        f"⚡️ <b>Енергія</b>: від <u>{MIN_ENERGY_CHRISTMAS_REWARD}</u> до <u>{MAX_ENERGY_CHRISTMAS_REWARD}</u>\n"
        f"💰 <b>Монети</b>: від <u>{MIN_MONEY_CHRISTMAS_REWARD}</u> до <u>{MAX_MONEY_CHRISTMAS_REWARD}</u>\n\n"
        "Не забудьте зайти завтра, адже подарунки з'являються щодня! 🎉"
            ),
        
        False : "Ви сьогодні вже отримали нагороду"
    }
    
    get_reward  = user_get_rewards(christmas_reward)
    
    keyboard = None
    if get_reward:
        keyboard = get_christmas_reward_keyboard()
    
    await message.answer_photo(
        photo = CHRISTMAS_TREE_PHOTO,
        caption = texts[get_reward],
        reply_markup = keyboard
    )
    
    
def user_get_rewards(christmas_reward: ChristmasReward | None) -> bool:
    if not christmas_reward:
        return True
    elif not christmas_reward.can_be_rewarded:
        return False
    else:
        return True
    

@get_reward_router.callback_query(
    F.data == "get_christmas_reward",
    CheckTimeChristmasTree()
)
async def get_reward_christmas_tree(
    query: CallbackQuery,
    character: Character
):
    async with UserLock(user_id=character.characters_user_id):
        reward = await ChristmasRewardService.get_christmas_reward(
            user_id = character.characters_user_id
        )
        if not reward:
            await ChristmasRewardService.create_christmas_reward(
                user_id = character.characters_user_id
            )
        get_reward  = user_get_rewards(reward)
        if not get_reward:
            return await query.answer(
                text = "Ви сьогодні вже отримали нагороду",
                show_alert = True
            )
        await ChristmasRewardService.update_time_get_reward(
            user_id = character.characters_user_id
        )
    await query.message.answer("Ви отримали 🎁 <b><u>новорічний кейс</u></b> 🎁, він буде автоматично відкритий через 5 секунд")
    await asyncio.sleep(5)
    message = await query.message.answer(
        text = ". . ."
    )
    open_box = OpenBox(cristmas_box.winner_items)
    frame_generator = open_box.get_next_frame()
    for num, frame in enumerate(frame_generator):
        if frame and num % 3 == 0:
            await message.edit_text(text=frame)
        await asyncio.sleep(0.3)

    await query.message.answer(
        text = (
            f"Вітаємо! Ви відкрили 🎁 новорічний кейс і отримали: "
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