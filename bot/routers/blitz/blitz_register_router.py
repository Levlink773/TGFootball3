import traceback

from aiogram import Router
from aiogram.types import CallbackQuery

from blitz.services.blitz_service import BlitzService
from blitz.exception import BlitzCloseError, CharacterExistsInBlitzError, BlitzDoesNotExistError, MaxUsersInBlitzError
from bot.callbacks.blitz_callback import BlitzRegisterCallback
from database.models.character import Character

blitz_register_router = Router()

@blitz_register_router.callback_query(BlitzRegisterCallback.filter())
async def blitz_register_filter(query: CallbackQuery,
                                callback_data: BlitzRegisterCallback,
                                character: Character,
                                ):
    try:
        await BlitzService.add_character_to_blitz(callback_data.blitz_id, character, callback_data.max_characters)
        text = "🎉 Ви успішно зареєструвалися на бліц-турнір! Очікуйте на початок в 15:00 та готуйтеся до боротьби ⚽️"
        await query.answer(
            text,
            show_alert=True,
        )
        await query.message.delete()
        await query.message.answer(text)
    except BlitzCloseError as e:
        text = "⌛️ Реєстрацію на бліц-турнір закрито. Чекайте завтра для наступної битви!"
        print(f"msg: {e}")
        await query.answer(text, show_alert=True)
        await query.message.delete()
    except CharacterExistsInBlitzError as e:
        print(f"msg: {e}")
        text = "🔔 Ви вже зареєстровані на цей бліц-турнір. Чекайте початку турніру!"
        await query.answer(text, show_alert=True)
        await query.message.delete()
        await query.message.answer(text)
    except MaxUsersInBlitzError as e:
        print(f"msg: {e}")
        text = (
            "❌ На жаль, реєстрація завершена — кількість учасників у бліц-турнірі вже досягла максимуму. \n\n"
            "📌 Слідкуйте за анонсами — новий турнір буде дуже скоро. Підготуйте свого гравця до наступного виклику! ⚔️⚽️"
        )
        await query.answer(text, show_alert=True)
        await query.message.delete()
        await query.message.answer(text)
    except BlitzDoesNotExistError as e:
        print(f"msg: {e}")
        await query.answer(
            f"❓ Турнір з id {callback_data.blitz_id} не знайдено. Перевірте, будь ласка, коректність даних.",
            show_alert=True,
        )
        await query.message.delete()
    except Exception as e:
        traceback.print_exc()
        print(f"msg: {e}")
        await query.answer(
            "⚠️ Упс! Сталася помилка при реєстрації на бліц-турнір. Спробуйте ще раз або зверніться до підтримки.",
            show_alert=True,
        )
        await query.message.delete()
