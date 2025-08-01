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
        await query.answer("Поздравляю вы успешно зарегестрровались на блиц турнир!")
    except BlitzCloseError as e:
        print(f"msg: {e}")
        await query.answer("Запись на Блиц турнир закрыта. Записуйся завтра до с 14:30 дл 15:00")
    except CharacterExistsInBlitzError as e:
        print(f"msg: {e}")
        await query.answer("You already participate in the blitz!")
    except BlitzDoesNotExistError as e:
        print(f"msg: {e}")
        await query.answer("Blitz with id {blitz_id} does not exist!")
    except Exception as e:
        traceback.print_exc()
        print(f"msg: {e}")
        await query.answer(f"Error: {e}")