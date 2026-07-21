from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models.character import Character
from services.reminder_character_service import RemniderCharacterService
from bot.keyboards.pvp_duels_keyboard import find_oponent_user_duel, leave_pool_find_oponent

from bot.filters.check_duel_filter import CheckDuelStatus
from pvp_duels.duel_core import CoreDuel
from pvp_duels.duel_manager import DuelManager
find_user_duel_router = Router()

@find_user_duel_router.message(F.text == "🥅 ПВП-пенальті")
async def find_user_duel_handler(message: Message, character: Character):
    return
    if character.reminder.character_in_duel:
        if not DuelManager.character_in_duel(character):
            await RemniderCharacterService.edit_status_duel_character(
                character_id=character.id,
                status=False
            )
        else:
            return message.answer("Ви вже в процессі ПВП-пеналті",
                                  reply_markup = leave_pool_find_oponent())
    
    await message.answer(
        text = """
<b>Пошук випадкового суперника</b> ⚔️

Готові вступити в битву на футбольному полі та перевірити свої сили?
Система автоматично підбере для вас гідного суперника Ніколи не знаєш, з ким зіткнешся - це може бути як рівний за силою гравець, так і справжній чемпіон, готовий кинути вам виклик.

<b>Почніть пошук і дізнайтеся, хто стане вашим ворогом сьогодні! Переможець отримає енергію!</b>
        """,
        reply_markup=find_oponent_user_duel()
    )
    
@find_user_duel_router.callback_query(F.data == "find_enemy_duel")
async def add_to_pool_finder_enemy_duel_handler(query: CallbackQuery, character: Character):
    if await CoreDuel.is_in_queue(character):
        return await query.message.edit_text("❌ <b>Ви вже в пошуку дуелі !</b>", 
                                          reply_markup = leave_pool_find_oponent())
    await CoreDuel.add_user_to_pool(character)
    await RemniderCharacterService.edit_status_duel_character(
        character_id=character.id, 
        status=True)
    await query.message.edit_text("""
Ви в пулі очікування! 🎯

Ми почали пошук гідного суперника для вашої футбольної дуелі. Це займе небагато часу - система підбирає противника, який готовий битися з вами

🕐 Чекайте - пошук може зайняти кілька секунд або хвилин, залежно від доступності гравців. У будь-який момент може з'явитися той, хто кине вам виклик!
Будьте готові! Скоро почнеться битва, і від вас вимагатиметься максимум енергії та концентрації.⚡

Якщо ви хочете вийти з пулу, нажміть кнопку знизу""",
    reply_markup= leave_pool_find_oponent()
    )
    
@find_user_duel_router.callback_query(F.data == "leave_pool_find_oponent")
async def leave_from_pool_find_enemy_duel_handler(query: CallbackQuery, character: Character):
    await CoreDuel.remove_user_from_pool(character)
    await RemniderCharacterService.edit_status_duel_character(
        character_id=character.id, 
        status=False)
    await query.message.edit_text("""
<b>Ви вийшли з пошуку супротивника!</b> 🚫

Ваш запит на пошук був скасований. Ви можете повернутися в гру в будь-який момент, щоб знайти нового супротивника та продовжити битву!
Не забувайте, що можливості для дуелей завжди поруч!""")