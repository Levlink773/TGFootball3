from typing import Tuple

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import EDUCATION_TASK
from database.models.character import Character
from services.character_service import CharacterService
from stats.stat import stat_done_already, BaseStatistics, STAT_REGISTRY
from stats.tier import _decode_indices, _generate_indices_for_all_tiers, _encode_indices, _safe_pick, TIER_LIST

education_task_router = Router()

async def _build_tasks_message_and_kb(character: Character) -> Tuple[str, InlineKeyboardMarkup]:
    kb = InlineKeyboardBuilder()
    btns = []

    # 1) Получаем/создаём cipher индексов
    indices = _decode_indices(getattr(character, "tier_cipher", "") or "", len(TIER_LIST))
    if not indices:
        indices = _generate_indices_for_all_tiers()
        character.tier_cipher = _encode_indices(indices)
        await CharacterService.edit_tier_cipher(character.id, character.tier_cipher)

    tier_blocks = []

    # 2) Для каждого Tier берём РОВНО ОДНУ задачу по индексу из cipher
    for tier_pos, (tier_name, stat_types) in enumerate(TIER_LIST):
        chosen_stat_type = _safe_pick(stat_types, indices[tier_pos])

        # стандартные три корзины
        not_done_lines = []
        done_with_reward_lines = []
        done_without_reward_lines = []

        stat_cls = STAT_REGISTRY[chosen_stat_type]
        stat_instance: BaseStatistics = stat_cls(character)

        done, _ = stat_instance.statistics_result()
        user_completed_types = {s.stat_type for s in character.statistics}
        already_recorded = chosen_stat_type in user_completed_types

        if not done:
            details = (
                f"🔸 Завдання: {stat_instance.description()}\n\n"
                f"📊 Ваш прогрес:\n{stat_instance.describe()}"
            )
            not_done_lines.append(f"<blockquote>{details}</blockquote>")
        else:
            if already_recorded:
                details = (
                    f"✔️ <b>{stat_instance.description()}</b>\n\n"
                    f"{stat_done_already.get(chosen_stat_type, 'Ви вже отримали нагороду за це завдання.')}"
                )
                done_with_reward_lines.append(f"<blockquote>{details}</blockquote>")
            else:
                details = (
                    f"🎉 <b>{stat_instance.description()}</b>\n\n"
                    f"{stat_instance.describe_statistics_success()}"
                )
                done_without_reward_lines.append(f"<blockquote>{details}</blockquote>")
                btns.append(
                    InlineKeyboardButton(
                        text=stat_instance.text_get_button(),
                        callback_data=f"claim_stat:{chosen_stat_type.value}"
                    )
                )

        # 3) собираем блок по Tier (всегда один выбранный таск на Tier)
        blocks = []
        if not_done_lines:
            blocks.append("⚡ <b>Активні завдання</b>\n\n" + "\n\n".join(not_done_lines))
        if done_with_reward_lines:
            blocks.append("✅ <b>Виконані завдання</b>\n\n" + "\n\n".join(done_with_reward_lines))
        if done_without_reward_lines:
            blocks.append("🎁 <b>Готові до отримання нагороди</b>\n\n" + "\n\n".join(done_without_reward_lines))

        tier_blocks.append(f"\n\n<b>{tier_name}</b>\n\n" + ("\n\n".join(blocks) if blocks else "Немає доступних завдань у цьому розділі."))

    # 4) Кнопки
    if btns:
        kb.row(*btns, width=1)
    kb.row(InlineKeyboardButton(text="⬅ Назад", callback_data="get_education_center"))

    # 5) Итоговый текст
    header = "<b>🎯 Завдання в освітньому центрі</b>"
    body = "\n\n".join(tier_blocks) if tier_blocks else "Немає доступних завдань."
    return f"{header}\n\n{body}", kb.as_markup()


@education_task_router.callback_query(F.data == "get_tasks_education_center")
async def get_tasks_education_cernter(query: CallbackQuery, character: Character):
    """
    Показуємо завдання згідно з tier_cipher:
    - cipher формат: "1,3,2" (1-based индексы в TIER_LIST для Tier1, Tier2, Tier3);
    - если cipher пуст, генерируем новый валидный.
    """
    await query.answer()
    text, kb = await _build_tasks_message_and_kb(character)
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=EDUCATION_TASK, caption=text),
            reply_markup=kb
        )
    except Exception:
        await query.message.answer_photo(photo=EDUCATION_TASK, caption=text, reply_markup=kb)


@education_task_router.callback_query(F.data.startswith("claim_stat:"))
async def claim_stat_callback(query: CallbackQuery, character: Character):
    """
    Обработка "Отримати": выдаём награду и помечаем статистику.
    """
    await query.answer()

    payload = query.data.split("claim_stat:", 1)
    if len(payload) < 2 or not payload[1]:
        await query.message.answer("Невірні дані заявки.")
        return

    stat_value = payload[1]
    target_type = None
    for st_type in STAT_REGISTRY.keys():
        if st_type.value == stat_value:
            target_type = st_type
            break

    if target_type is None:
        await query.message.answer("Невідома статистика.")
        return

    stats_cls = STAT_REGISTRY[target_type]
    stats_instance = stats_cls(character)

    done, _ = stats_instance.statistics_result()
    user_completed_types = {s.stat_type for s in character.statistics}
    already_recorded = target_type in user_completed_types

    if not done:
        await query.message.answer("Ви ще не виконали цю задачу.")
        return

    if already_recorded:
        await query.message.answer("Нагорода вже була отримана раніше.")
        return

    try:
        await stats_instance.reward_stat(query.message)
    except Exception as e:
        await query.message.answer(f"Помилка при видачі нагороди: {e}")
        return

    await query.message.answer("Нагорода успішно отримана 🎉")
