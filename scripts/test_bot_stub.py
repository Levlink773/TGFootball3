"""Minimal test bot (@testbottgfootball_bot): /start -> button opening the Mini App.

No game logic, no schedulers, no DB writes — safe to run beside the prod bot.
Used only for the test-bot phase of the Mini App rollout.
"""
import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
from dotenv import load_dotenv

load_dotenv()

WEBAPP_URL = os.getenv("WEBAPP_ORIGIN", "https://app.football-blitz.online")

bot = Bot(os.environ["TEST_BOT_TOKEN"])
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="⚽ Відкрити гру",
                web_app=WebAppInfo(url=WEBAPP_URL),
            )
        ]]
    )
    await message.answer(
        "Тестовий бот TG Football.\nТисни кнопку, щоб відкрити Mini App:",
        reply_markup=keyboard,
    )


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
