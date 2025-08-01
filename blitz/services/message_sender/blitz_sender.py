import traceback

from aiogram.types import InlineKeyboardMarkup

from blitz.services.blitz_team_service import BlitzTeamService
from database.models.blitz_team import BlitzTeam
from database.models.character import Character
from loader import bot


async def send_message(character: Character, text: str, reply_markup: InlineKeyboardMarkup = None):
    try:
        if character.is_bot:
            return

        await bot.send_message(
            chat_id=character.characters_user_id,
            text=text,
            reply_markup=reply_markup
        )
    except Exception as E:
        traceback.print_exc()
        print(E)


async def send_message_all_characters(characters: list[Character], text: str, reply_markup: InlineKeyboardMarkup = None):
    for character in characters:
        await send_message(character, text, reply_markup)


class BlitzTeamSender:
    @classmethod
    async def send_team_message(cls, team: BlitzTeam):
        character1, character2 = await BlitzTeamService.get_characters_from_blitz_team(team)
        await bot.send_message(character1.characters_user_id, f"Ваш командный игрок {character2.owner.user_name}.")
        await bot.send_message(character2.characters_user_id, f"Ваш командный игрок {character1.owner.user_name}.")
    @classmethod
    async def send_teams_message(cls, teams: list[BlitzTeam]):
        for team in teams:
            await BlitzTeamSender.send_team_message(team)