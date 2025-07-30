from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.league_keyboard import keyboard_menu_league

from constants import PHOTO_MENU_MATCHES

menu_league_router = Router()


TEXT_TEMPLATE_MENU_MATCHES = """
🏟️ Матчі —
Це центр подій гри — тут проходять щоденні матчі регулярної ліги, Кубку України, Новачків, та головного трофею гри - Єврокубків! 
 Саме тут твоя команда змагається з іншими за очки, рейтинг і славу! ⚽️🔥

📅 Матчі відбуваються щодня — встигни взяти участь, щоб принести команді перемогу!

👉 Вступай у матчі просто зараз — твої партнери вже на полі!<b><i> </i>Стадіон-ліга - зареєструватися в матч</b>
"""

@menu_league_router.message(
    F.text.regexp(r"(✅\s*)?⚽️ Матчі(\s*✅)?"),
)
async def menu_league(
    message: Message,
    state: FSMContext
):  
    await state.clear()
    await message.answer_photo(
        photo=PHOTO_MENU_MATCHES,
        caption=TEXT_TEMPLATE_MENU_MATCHES,
        reply_markup=keyboard_menu_league()
    )