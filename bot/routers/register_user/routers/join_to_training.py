import asyncio
from datetime import datetime, timedelta
from aiogram import F, Router
from aiogram.types import (
    Message, 
    CallbackQuery,
)

from database.models.user_bot import STATUS_USER_REGISTER
from database.models.character import Character
from database.events.event_new_member_exp import EXP_CONSTANT
from bot.keyboards.menu_keyboard import main_menu
from bot.routers.register_user.config import (
    PHOTO_STAGE_REGISTER_USER,
    TEXT_STAGE_REGISTER_USER
)
from bot.callbacks.gym_calbacks import SelectGymType

from schedulers.scheduler_gym_rasks import GymScheduler
from services.user_service import UserService
from services.reminder_character_service import RemniderCharacterService
from services.club_infrastructure_service import ClubInfrastructureService

from constants import (
    const_name_characteristics,
    TOTAL_POINTS_ADD_NEW_MEMBER,
    PHOTO_NEW_BONUS_MEMBER_HAR,
    GYM_PHOTO
)

from ..message_new_member import SendMessageNewMember
from .new_member_bonus import get_new_member_bonus_handler
from .claim_training_center import claim_training_center_handler

first_training_router = Router()

TEMPLATE_STARTER_POWER_POINTS = f"""
🎉 <b>Вітаємо в грі, новачку!</b> 

За свій перший крок ти отримуєш <u>{TOTAL_POINTS_ADD_NEW_MEMBER} очок Сили</u> — твій стартовий бонус! 🚀

Що далі?
⚡ Використовуй Силу на тренування і матчі
🏆 Розвивайся і ставай сильнішим щодня

<b>І пам'ятай:</b> коли збереш <u>{EXP_CONSTANT} Досвіду</u>, на тебе чекатиме спеціальний <b>Бокс з нагородами</b>! 🎁

<b>Твоя пригода тільки починається. Вперед до перемог!</b> 🔥
"""

TEXT_LAST_STEP = """
🔹 <b>Тренер:</b>
— Ось і все, чемпіоне! Ти готовий до справжньої гри. ⚽️🔥
Тепер головне — не зупиняйся:

✅ <b>Вступай у матчі</b> — тисни кнопку <b>"Матчі"</b> → <b>"Матчі ліги"</b>, старт о 21:00 кожен день.
✅ <b>Тренуйся щодня</b>, щоб покращувати свого гравця — кнопка <b>"Тренування"</b>
✅ <b>І обов’язково приєднуйся до нашої спільноти:</b>
👉 <a href="https://t.me/tgfootballchat/2">ЧАТ- Спільнота</a> — тут тобі завжди допоможуть, підкажуть і підтримають!

<b>Удачі на полі! 💪</b>
Пам’ятай: <i>справжні легенди виростають з першого матчу.</i>
"""

TEXT_SECOND_STEP = """
✅ Останній крок перед грою!

Ти вже майже на полі — залишилось зовсім трохи:

⚽️ Зареєструйся в матч — сьогодні о 21:00
📍 Матчі → Стадіон → Ліга

💬 Приєднуйся до спільноти гравців:
👉 Загальний чат та чат своєї команди — у розділі "Спілкування"

🎯 Готово? Тепер ти повноцінний гравець. Вперед до першої перемоги! 💪
"""


async def join_to_training(
    message: Message,
    character: Character
) -> None:
    await asyncio.sleep(6)
    new_status = STATUS_USER_REGISTER.FIRST_TRAINING
    
    await UserService.edit_status_register(
        user_id=character.characters_user_id,
        status=new_status
    )
    user = await UserService.get_user(
        user_id=character.characters_user_id
    )
    await message.answer_photo(
        caption = TEXT_STAGE_REGISTER_USER[new_status],
        photo   = PHOTO_STAGE_REGISTER_USER[new_status],
        reply_markup = main_menu(user)
    )


@first_training_router.callback_query(
    SelectGymType.filter(
        F.new_user == True
    )
)
async def select_gym_type_first_training(
    query: CallbackQuery,
    callback_data: SelectGymType,
    character: Character
) -> None:
    gym_type = callback_data.gym_type
    
    await query.message.delete()
    gym_time = timedelta(minutes=5)
    club_infrastructure = None
    if character.club_id:
        club_infrastructure = await ClubInfrastructureService.get_infrastructure(character.club_id)
    gym_scheduler = GymScheduler(
        character        = character,
        type_characteristic = gym_type,
        time_training       = gym_time,
        club_infrastructure = club_infrastructure
    )
    gym_scheduler.start_training()
    await RemniderCharacterService.update_training_info(
        character_id          = character.id,
        training_stats        = gym_type,
        time_start_training   = datetime.now(),
        time_training_seconds = gym_time.total_seconds()
    )
    await RemniderCharacterService.toggle_character_training_status(
        character_id=character.id,   
    )
    await claim_training_center_handler(
        character=character
    )
    # await SendMessageNewMember.send_message(character=character)
    # await asyncio.sleep(6)
    # asyncio.create_task(send_message_first_step(query, character))
    # asyncio.create_task(send_message_second_step(query.message))
    # asyncio.create_task(send_message_last_step(query.message))
    
# async def send_message_first_step(
#     query: CallbackQuery,
#     character: Character
# ):
#     await asyncio.sleep(15)
#     await query.message.answer_photo(
#         photo=PHOTO_NEW_BONUS_MEMBER_HAR,
#         caption = TEMPLATE_STARTER_POWER_POINTS,
#     )
#     await get_new_member_bonus_handler(
#         query,
#         character
#     )
    
# async def send_message_second_step(
#     message: Message
# ):
#     await asyncio.sleep(45)
#     await message.answer(
#         text = TEXT_SECOND_STEP
#     )

# async def send_message_last_step(
#     message: Message
# ):
#     await asyncio.sleep(310)
#     await message.answer(
#         text = TEXT_LAST_STEP
#     )