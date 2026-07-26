"""Единая отправка проактивных уведомлений: deep-link кнопка + пометка блокировки.

ponytail: это НЕ фреймворк уведомлений — 3 функции. Тексты живут рядом с кодом,
который их шлёт (как везде в проекте), таблицы логов доставки нет.
Потолок: существующие отправщики (blitz_sender, league/user_sender,
training/sender/*) сюда НЕ переведены и по-прежнему бьют в заблокированных
юзеров. Upgrade path: провести их через notify() тем же вызовом.
"""

from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from config import WEBAPP_ORIGIN
from loader import bot
from services.character_service import CharacterService
from utils.rate_limitter import rate_limiter
from logging_config import logger

# Ровно ключи SCREENS из webapp/src/App.jsx. Новый экран — сначала туда.
SCREENS = frozenset({
    "home", "player", "matches", "training", "league",
    "fame", "shop", "settings", "team", "stats", "trainer",
})


def webapp_button(screen: str, text: str) -> InlineKeyboardMarkup | None:
    """Кнопка, открывающая Mini App на конкретном экране.

    None, если WEBAPP_ORIGIN не задан (dev) или экран неизвестен — отправка
    уведомления не должна падать из-за отсутствующей кнопки.
    """
    if not WEBAPP_ORIGIN or screen not in SCREENS:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=text,
            web_app=WebAppInfo(url=f"{WEBAPP_ORIGIN}?screen={screen}"),
        )
    ]])


@rate_limiter
async def notify(character, text: str, screen: str = None, button_text: str = None) -> bool:
    """Отправить DM персонажу. True — доставлено.

    TelegramForbiddenError ловим ВНУТРИ обёрнутой функции: rate_limiter.__call__
    глотает любые исключения кроме TelegramRetryAfter, снаружи мы бы её не увидели.
    """
    if character.is_bot or character.is_blocked or not character.characters_user_id:
        return False
    try:
        await bot.send_message(
            chat_id=character.characters_user_id,
            text=text,
            reply_markup=webapp_button(screen, button_text) if screen and button_text else None,
        )
        return True
    except TelegramForbiddenError:
        await CharacterService.mark_blocked(character.id)
        logger.info(f"User {character.characters_user_id} blocked the bot — marked is_blocked")
        return False
    except Exception as e:
        logger.error(f"Failed notify to {character.characters_user_id}: {e}")
        return False


async def notify_many(characters, text, screen: str = None, button_text: str = None) -> int:
    """Разослать списку персонажей. text — строка или callable() -> строка
    (для ротации вариантов). Возвращает число доставленных.
    """
    sent = 0
    for character in characters:
        body = text() if callable(text) else text
        if await notify(character, body, screen=screen, button_text=button_text):
            sent += 1
    return sent
