from aiogram import Router
from aiogram import Bot, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command

from bot.keyboards.menu_keyboard import main_menu, test
from bot.routers.register_user.start_register_user import StartRegisterUser
from bot.routers.register_user.routers.join_to_club import join_to_club

from database.models.user_bot import UserBot, STATUS_USER_REGISTER
from services.user_service import UserService
from services.character_service import CharacterService

from loader import bot

from constants import PLOSHA_PEREMOGU
from config import VIDEO_ID

start_router = Router()

@start_router.message(CommandStart())
async def start_command_handler(
    message: Message, 
    state: FSMContext, 
    user: UserBot, 
    command: Command    
):
    
    if command.args:
        await register_referal(user=user, referal=command.args) 
    if not user.end_register:
        if user.status_register == STATUS_USER_REGISTER.PRE_RIGSTER_STATUS:
            start_register = StartRegisterUser(
                user = user
            )
            return await start_register.start_register_user()
        if user.status_register == STATUS_USER_REGISTER.JOIN_TO_CLUB:
            character = await CharacterService.get_character(
                character_user_id = user.user_id
            )
            return await join_to_club(
                message=message,
                character=character,
                state=state,
                is_sleep=False
            )
        
        
    video_start = FSInputFile("src/start_video.MP4",filename="video_start") if not VIDEO_ID else VIDEO_ID

    await state.clear()
    bot_name = await message.bot.get_my_name()
    text = f"""
<b>Вітаємо у «{bot_name.name} — життя футболіста онлайн-гра!»</b> ⚽️✨
Найкращий симулятор кар'єри футболіста! Тут ви зможете пройти шлях від молодого таланта до легенди світового футболу.

<b>Розвивайте свої навички 🏋️‍♂️</b>
Прокачуйте персонажа, приєднуйтесь до команд та інших гравців. Беріть участь у великих турнірах і ведіть свою команду до перемоги 🏆!

<b>Ваші рішення на полі та за його межами</b> 🏅
Вони визначать долю вашої кар'єри. Кожен вибір, кожен матч — це крок до футбольної величі.

<b>Готові стати новою зіркою футболу? 🌟</b>
Час почати свою подорож до слави!

🔽<b>НАТИСКАЙ КНОПКУ СТВОРИТИ ПЕРСОНАЖА</b>🔽
    """
    
    message = await message.answer_video(
        video=video_start,
        caption=text,
        reply_markup=main_menu(user)
    )


async def register_referal(user: UserBot, referal: str):
    if not "ref_" in referal:
        return
    referal_user_id = referal.split("ref_")[1]
    await UserService.add_referal_user_id(
        my_user_id=user.user_id,
        referal_user_id= referal_user_id
    )
    try:
        mess = await bot.send_message(
            chat_id=referal_user_id,
            text=f"🎉 <b>У вас з'явився новий реферал!</b>\n\n{user.link_to_user}")
    except:
        pass
    


@start_router.message(F.text == "⬅️ Головна площа")
async def plosha(message: Message, user: UserBot):
    await message.answer_photo(photo = PLOSHA_PEREMOGU, 
                               caption=f"""
Вітаю тебе на головній площі гри! Місце де ти можеш обрати основні функції:
<b>Стадіон</b> - реєстрація на матч та таблиці
<b>Тренажерний зал</b> - місце прокачки персонажа
<b>Навчальний центр</b> - досвід та заробіток монет.
<b>Тренувальна база</b> - покращення команди перед грою
<b>Магазин</b> - тут можна купити речі задля покращення футболіста.

                            
                               """,
                               reply_markup=main_menu(user))

