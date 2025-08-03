import traceback

from aiogram import Router
from aiogram.types import CallbackQuery

from blitz.services.blitz_service import BlitzService
from blitz.exception import BlitzCloseError, CharacterExistsInBlitzError, BlitzDoesNotExistError
from bot.callbacks.blitz_callback import BlitzRegisterCallback
from database.models.character import Character

router = Router()

@router.callback_query(BlitzRegisterCallback.filter())
async def blitz_register_filter(query: CallbackQuery,
                                callback_data: BlitzRegisterCallback,
                                character: Character,
                                ):
    try:
        await BlitzService.add_character_to_blitz(callback_data.blitz_id, character)
        await query.answer(
            "🎉 Ви успішно зареєструвалися на бліц-турнір! Очікуйте на початок в 15:00 та готуйтеся до боротьби ⚽️"
        )
    except BlitzCloseError as e:
        print(f"msg: {e}")
        await query.answer(
            "⌛️ Реєстрацію на бліц-турнір закрито. Чекайте завтра для наступної битви!"
        )
    except CharacterExistsInBlitzError as e:
        print(f"msg: {e}")
        await query.answer(
            "🔔 Ви вже зареєстровані на цей бліц-турнір. Чекайте початку турніру!"
        )
    except BlitzDoesNotExistError as e:
        print(f"msg: {e}")
        await query.answer(
            f"❓ Турнір з id {callback_data.blitz_id} не знайдено. Перевірте, будь ласка, коректність даних."
        )
    except Exception as e:
        traceback.print_exc()
        print(f"msg: {e}")
        await query.answer(
            "⚠️ Упс! Сталася помилка при реєстрації на бліц-турнір. Спробуйте ще раз або зверніться до підтримки."
        )
