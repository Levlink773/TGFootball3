import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from datetime import datetime

from bot.keyboards.gym_keyboard import menu_education_cernter
from bot.club_infrastructure.types import InfrastructureType
from bot.club_infrastructure.utils import calculate_bonus_by_character

from constants import GET_RANDOM_NUMBER, DELTA_TIME_EDUCATION_REWARD, EDUCATION_CENTER
from constants import X2_REWARD_WEEKEND_START_DAY, X2_REWARD_WEEKEND_END_DAY

from database.models.character import Character
from database.models.user_bot import STATUS_USER_REGISTER

from services.character_service import CharacterService
from services.user_service import UserService

from schedulers.scheduler_education import EducationRewardReminderScheduler

from utils.club_utils import get_text_education_center_reward


education_center_router = Router()
EDUCATION_TEXT = "Ласкаво просимо до навчального центру\nТут Ви можете отримати досвід задля покращення рівня гравця, та отримати монети за вдале навчання, кожні 12 годин! "
@education_center_router.message(
    F.text.regexp(r"(✅\s*)?🏫 Навчальний центр(\s*✅)?")
)
async def go_to_gym(message: Message):
    await message.answer_photo(photo=EDUCATION_CENTER,
        caption=EDUCATION_TEXT, reply_markup=menu_education_cernter()
        )

@education_center_router.callback_query(
    F.data == "get_education_center",
)
async def go_to_gym(query: CallbackQuery):
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=EDUCATION_CENTER, caption=EDUCATION_TEXT),
            reply_markup=menu_education_cernter()
        )
    except Exception as e:
        await query.message.answer_photo(
            photo=EDUCATION_CENTER,
            caption=EDUCATION_TEXT,
            reply_markup=menu_education_cernter()
        )
locks_by_character_id: dict[int, asyncio.Lock] = {}

@education_center_router.callback_query(F.data == "get_rewards_education_center")
async def get_rewards_education_cernter(query: CallbackQuery, character: Character):
    lock = locks_by_character_id.setdefault(character.id, asyncio.Lock())
    if lock.locked():
        return await query.message.answer("<b>⏳ Обробка нагороди вже триває. Зачекайте...</b>")
    async with lock:
        if not datetime.now() > character.reminder.education_reward_date:
            time_to_get_reward = character.reminder.education_reward_date - datetime.now()
            hours, remainder = divmod(time_to_get_reward.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return await query.message.answer(f"<b>Залишилося часу до отримання нагороди: {hours} год {minutes} хв</b>")

        exp, coins, energy = await calculation_bonus(character)

        await CharacterService.edit_character_energy(
            character_id = character.id,
            amount_energy = energy
        )

        await CharacterService.update_character_education_time(
            character=character,
            amount_add_time=DELTA_TIME_EDUCATION_REWARD
        )

        await CharacterService.add_exp_character(
            character_id=character.id,
            amount_exp_add=exp
        )

        await CharacterService.update_money_character(
            character_id=character.id,
            amount_money_adjustment=coins
        )

        # Перевзводить напоминание вручную больше не нужно: почасовой sweep в
        # schedulers/scheduler_education.py сам находит всех, у кого подошёл
        # education_reward_date. Это же чинит клейм из Mini App, который из
        # отдельного процесса перевзвести DateTrigger не мог.

        await query.message.answer(
            get_text_education_center_reward(
                exp=exp,
                coins=coins,
                energy=energy,
                delta_time_education_reward=DELTA_TIME_EDUCATION_REWARD
            )
        )

        user = await UserService.get_user(character.characters_user_id)

        if user.status_register == STATUS_USER_REGISTER.TRAINING_CENTER:
            from bot.routers.register_user.routers.buy_first_equipment import buy_first_equipment_handler
            await buy_first_equipment_handler(character)
    
async def calculation_bonus(character: Character) -> tuple[int, int, int]:

    exp = GET_RANDOM_NUMBER(1, 3)
    coins = GET_RANDOM_NUMBER(5, 10)
    energy = GET_RANDOM_NUMBER(30, 50)

    bonus_multiplier = 1
    exp, coins, energy = await calculate_bonus_by_character(
        character,
        InfrastructureType.TRAINING_CENTER,
        exp,
        coins,
        energy
    )
    if (
        X2_REWARD_WEEKEND_START_DAY <= datetime.now().day <= X2_REWARD_WEEKEND_END_DAY
        or character.vip_pass_is_active
    ):
        bonus_multiplier *= 2

    exp, coins, energy = apply_multiplier((exp, coins, energy), bonus_multiplier)

    return int(exp), int(coins), int(energy)


def apply_multiplier(rewards: tuple[int, int, int], multiplier: int) -> tuple[int, int, int]:
    return tuple(value * multiplier for value in rewards)