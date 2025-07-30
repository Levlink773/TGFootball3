
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from bot.filters.check_admin_filter import CheckUserIsAdmin


get_logger_router = Router()

LOG_FILE_PATH = 'error_logs.log'

@get_logger_router.message(Command("get_logs"), CheckUserIsAdmin())
async def get_logger(message: Message):
    
    try:
        log_file = FSInputFile(LOG_FILE_PATH)
        await message.answer_document(
            document=log_file,
            caption="логи ошибок",
        )
    except FileNotFoundError:
        await message.answer("Лог файл не найден.")
        await message.answer("Ошибка при попытке отправить файл.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при отправке логов: {e}")