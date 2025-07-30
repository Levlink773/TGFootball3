from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.models.character import Character
from services.character_service import CharacterService

from bot.keyboards.gym_keyboard import no_energy_keyboard
from bot.callbacks.pvp_duel_callbacks import (
    SelectEnergyBit,
    SelectPositionAngle)

from pvp_duels.duel_manager import DuelManager
from pvp_duels.types import RoleDuel, PositionAngle

text_angle = {
    PositionAngle.UP    : "[⬆️ <b>верхній кут</b>]",
    PositionAngle.RIGHT : "[➡️ <b>правий кут</b>]",
    PositionAngle.LEFT  : "[⬅️ <b>лівий кут</b>]",
}

text_roles = {
    RoleDuel.FORWARD: (
        "Ви вибрали удар у {select_angle}! ⚽\n"
        "Тепер усе залежить від вашої майстерності та реакції воротаря. "
        "Чи готові ви відправити м'яч у сітку? 🥅"
    ),
    RoleDuel.GOALKEEPER: (
        "Ви вибрали відбити м'яч у {select_angle}! 🛡️\n"
        "Тепер ваше рішення буде перевірено — зможете ви зупинити удар суперника? 🤔"
    )
}

procesing_duel_router = Router()

@procesing_duel_router.callback_query(SelectEnergyBit.filter())
async def select_bit_user(query: CallbackQuery, character: Character, callback_data: SelectEnergyBit):
    pvp_duel = DuelManager.get_duel_by_id(callback_data.duel_id)

    if not pvp_duel:
        return await query.message.answer("❌ <b>Дуель не знайдено</b>")

    if callback_data.count_energy > character.current_energy:
        return await query.message.answer(
            text = "У вас не вистачає енергії, ви можете купити енергію в Крамниці енергії",
            reply_markup = no_energy_keyboard()
        ) 

    is_user_1 = character.id == pvp_duel.user_1.id
    if (is_user_1 and pvp_duel.bid_user_1) or (not is_user_1 and pvp_duel.bid_user_2):
        return await query.message.answer("✅ Ви вже зробили ставку")

    if is_user_1:
        pvp_duel.bid_user_1 = callback_data.count_energy
    else:
        pvp_duel.bid_user_2 = callback_data.count_energy

    await CharacterService.consume_energy(
        character_id=character.id,
        energy_consumed=callback_data.count_energy
    )

    await query.message.edit_reply_markup(reply_markup=None)
    await query.message.answer(f"<b>Ви зробили ставку</b> в 🔋 {callback_data.count_energy} енергії")

@procesing_duel_router.callback_query(SelectPositionAngle.filter())
async def select_bit_user(query: CallbackQuery, character: Character, callback_data: SelectPositionAngle):

    pvp_duel = DuelManager.get_duel_by_id(callback_data.duel_id)

    if not pvp_duel:
        return await query.message.answer("❌ <b>Дуель не знайдено</b>")

    is_user_1 = character.id == pvp_duel.user_1.id
    if (is_user_1 and pvp_duel.position_angle_user_1) or (not is_user_1 and pvp_duel.position_angle_user_2):
        return await query.message.answer("✅ Ви вже обрали сторону")

    if is_user_1:
        pvp_duel.position_angle_user_1 = callback_data.position_angle
    else:
        pvp_duel.position_angle_user_2 = callback_data.position_angle
        
    my_role = pvp_duel.get_role_by_user(character)
    
    await query.message.edit_text(
        text=text_roles[my_role].format(select_angle = text_angle[callback_data.position_angle]),
        reply_markup=None
    )