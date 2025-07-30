from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.callbacks.club_callbacks import InvoiceClubCallback
from bot.filters.check_admin_club_filter import CheckOwnerClub

from services.club_service import ClubService
from services.character_service import CharacterService

from logging_config import logger

from loader import bot

club_invoices_router = Router()


@club_invoices_router.callback_query(
    InvoiceClubCallback.filter(F.is_approved == True),
    CheckOwnerClub()
)
async def approve_invoice(
    query: CallbackQuery,
    callback_data: InvoiceClubCallback,
) -> None:
    club = await ClubService.get_club(club_id=callback_data.club_id)
    if not club:
        return await query.answer("Клуб не найден", show_alert=True)

    user_how_join = await CharacterService.get_character_by_id(
        character_id=callback_data.character_id
    )
    if user_how_join.club_id:
        return await query.answer("Игрок уже в клубе", show_alert=True)
    
    if not user_how_join:
        return await query.answer("Игрок не найден", show_alert=True)

    if len(club.characters) >= 11:
        return await query.answer("Клуб уже полон", show_alert=True)
    
    await CharacterService.update_character_club_id(
        character=user_how_join,
        club_id=club.id
    )

    await query.message.edit_reply_markup()
    await query.answer("Игрок успешно добавлен в клуб")
    await bot.send_message(
        chat_id=user_how_join.characters_user_id,
        text=f"Вы успешно вступили в клуб {club.name_club}!"
    )


@club_invoices_router.callback_query(
    InvoiceClubCallback.filter(F.is_approved == False),
    CheckOwnerClub()
)
async def decline_invoice(
    query: CallbackQuery,
    callback_data: InvoiceClubCallback,
) -> None:
    try:
        club = await ClubService.get_club(club_id=callback_data.club_id)
        if not club:
            return await query.answer("Клуб не найден", show_alert=True)

        user_how_join = await CharacterService.get_character_by_id(
            character_id=callback_data.character_id
        )
        
        if not user_how_join:
            return await query.answer("Игрок не найден", show_alert=True)

        await query.message.edit_reply_markup()
        await query.answer("Игрок отклонен", show_alert=True)
        await bot.send_message(
            chat_id=user_how_join.characters_user_id,
            text=f"Ваш запрос на вступление в клуб {club.name_club} был отклонен."
        )
    except Exception as e:
        await query.answer("Произошла ошибка при отклонении запроса", show_alert=True)
        logger.error(f"Ошибка при отклонении запроса на вступление в клуб: {e}")
    finally:
        await query.message.delete()
