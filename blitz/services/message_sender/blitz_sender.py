import traceback

from aiogram.types import InlineKeyboardMarkup

from blitz.blitz_match.constans import TEAM_BLITZ_PHOTO
from blitz.services.blitz_team_service import BlitzTeamService
from blitz.services.message_sender.rate_limiter import rate_limiter_simple
from database.models.blitz_team import BlitzTeam
from database.models.character import Character
from loader import bot
from utils.photo_utils import get_photo, save_photo_id


@rate_limiter_simple
async def send_message(character: Character, text: str, reply_markup: InlineKeyboardMarkup = None,
                       photo_path: str = None):
    try:
        if character.is_bot:
            return
        if photo_path:
            is_save, photo = await get_photo(photo_path)
            msg = await bot.send_photo(
                photo=photo,
                chat_id=character.characters_user_id,
                caption=text,
                reply_markup=reply_markup
            )
            if msg and not is_save:
                await save_photo_id(
                    patch_to_photo=photo_path,
                    photo_id=msg.photo[0].file_id,
                )
            return
        await bot.send_message(
            chat_id=character.characters_user_id,
            text=text,
            reply_markup=reply_markup
        )
    except Exception as E:
        traceback.print_exc()
        print(E)


async def send_message_all_characters(characters: list[Character], text: str, reply_markup: InlineKeyboardMarkup = None,
                                      photo_path: str = None):
    for character in characters:
        await send_message(character, text, reply_markup, photo_path)


class BlitzTeamSender:
    @classmethod
    async def send_team_message(cls, team: BlitzTeam):
        character1, character2 = await BlitzTeamService.get_characters_from_blitz_team(team)
        text1 = (
            f"🤝 Ваша команда сформована, ви в команді «{team.name}»! Ваш напарник: <b>{f'@{character2.owner.user_name}' if character2.owner.user_name else character2.name}</b>."
            "⏱️ У вас є 1 хвилина, щоб розробити ідеальну тактику для бліц-турніру. Нехай кожен пас і удар будуть точними! 💥"
        )
        text2 = (
            f"🤝 Ваша команда сформована, ви в команді «{team.name}»! Ваш напарник: <b>{f'@{character1.owner.user_name}' if character1.owner.user_name else character1.name}</b>."
            "⏱️ У вас є 1 хвилина на узгодження стратегії для бліц-турніру. Покажіть командний дух і здобудьте перемогу! 🏆"
        )
        await send_message(character1, text1,  photo_path=TEAM_BLITZ_PHOTO)
        await send_message(character2, text2, photo_path=TEAM_BLITZ_PHOTO)

    @classmethod
    async def send_teams_message(cls, teams: list[BlitzTeam]):
        for team in teams:
            await BlitzTeamSender.send_team_message(team)
