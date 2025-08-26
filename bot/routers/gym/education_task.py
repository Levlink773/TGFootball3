from typing import Tuple

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import EDUCATION_TASK
from database.models.character import Character
from stats.stat import stat_done_already, BaseStatistics, STAT_REGISTRY

education_task_router = Router()


def _build_tasks_message_and_kb(character: Character) -> Tuple[str, InlineKeyboardMarkup]:
    kb = InlineKeyboardBuilder()
    btns = []

    not_done_lines = []
    done_with_reward_lines = []
    done_without_reward_lines = []

    for st_type, stat_cls in  STAT_REGISTRY.items():
        stat_instance: BaseStatistics = stat_cls(character)
        done, progress = stat_instance.statistics_result()
        user_completed_types = {s.stat_type for s in character.statistics}
        already_recorded = st_type in user_completed_types

        if not done:
            # --- БЛОК 1: ЗАДАНИЯ В ПРОЦЕССЕ ---
            details = (
                f"🔸 Завдання: {stat_instance.description()}\n\n"
                f"📊 Ваш прогрес:\n{stat_instance.describe()}"
            )
            not_done_lines.append(
                f"<blockquote>{details}</blockquote>"
            )
        else:
            if already_recorded:
                # --- БЛОК 2: ЗАДАНИЯ ВЫПОЛНЕНЫ (НАГРАДА ПОЛУЧЕНА) ---
                details = (
                    f"✔️ <b>{stat_instance.description()}</b>\n\n"
                    f"{stat_done_already.get(st_type, 'Ви вже отримали нагороду за це завдання.')}"
                )
                done_with_reward_lines.append(
                    f"<blockquote>{details}</blockquote>"
                )
            else:
                # --- БЛОК 3: ЗАДАНИЯ ВЫПОЛНЕНЫ (ГОТОВЫ К НАГРАДЕ) ---
                details = (
                    f"🎉 <b>{stat_instance.description()}</b>\n\n"
                    f"{stat_instance.describe_statistics_success()}"
                )
                done_without_reward_lines.append(
                    f"<blockquote>{details}</blockquote>"
                )
                btns.append(InlineKeyboardButton(
                    text=stat_instance.text_get_button(),
                    callback_data=f"claim_stat:{st_type.value}"
                ))

    # Формируем блоки текста с разделами
    blocks = []
    if not_done_lines:
        blocks.append("⚡ <b>Активні завдання</b>\n\n" + "\n\n".join(not_done_lines))
    if done_with_reward_lines:
        blocks.append("✅ <b>Виконані завдання</b>\n\n" + "\n\n".join(done_with_reward_lines))
    if done_without_reward_lines:
        blocks.append("🎁 <b>Готові до отримання нагороди</b>\n\n" + "\n\n".join(done_without_reward_lines))

    # Кнопки
    if btns:
        kb.row(*btns, width=1)
    kb.row(InlineKeyboardButton(text="⬅ Назад", callback_data="get_education_center"))

    # Итоговое сообщение
    header = "<b>🎯 Завдання в освітньому центрі</b>"
    body = "\n\n".join(blocks) if blocks else "Немає доступних завдань."

    return f"{header}\n\n{body}", kb.as_markup()








@education_task_router.callback_query(F.data == "get_tasks_education_center")
async def get_tasks_education_cernter(query: CallbackQuery, character: Character):
    """
    Показываем все задания, их статусы и кнопки для получения наград (если есть).
    """
    await query.answer()  # скрываем 'крутилку' у клиента
    text, kb = _build_tasks_message_and_kb(character)
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
    Обработка нажатия на кнопку "Отримати" — выдаём награду и помечаем статистику.
    callback_data expected: "claim_stat:<STAT_VALUE>"
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

    stats_cls =  STAT_REGISTRY[target_type]
    stats_instance = stats_cls(character)

    done, progress = stats_instance.statistics_result()
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
