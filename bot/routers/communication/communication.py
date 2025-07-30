from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database.models.character import Character

from config import LINK_TO_CHAT

communication_router = Router()

TEXT_TEMPLATE = """
Чат для спілкування - <a href="{LINK_TO_CHAT}">*клік*</a>
{text_club_chat}
"""

TEXT_CHAT = """
Чат команды - <a href="{LINK_TO_CLUB_CHAT}">*клік*</a>
"""


@communication_router.message(
    F.text.regexp(r"(✅\s*)?🗣 Cпілкування(\s*✅)?")
)
async def communication_handler(
    message: Message, 
    state: FSMContext, 
    character: Character
):
    await state.clear()
    text_chat_club = ""
    if character.club:
        text_chat_club = TEXT_CHAT.format(
            LINK_TO_CLUB_CHAT=character.club.link_to_chat
        )
    text = TEXT_TEMPLATE.format(
        LINK_TO_CHAT=LINK_TO_CHAT,
        text_club_chat = text_chat_club
    )
        
    await message.answer(text)