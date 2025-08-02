from abc import ABC, abstractmethod

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from blitz.services.blitz_character_service import BlitzCharacterService
from bot.callbacks.blitz_callback import BoxRewardCallback
from database.models.blitz_team import BlitzTeam
from database.models.character import Character
from loader import bot
from services.character_service import CharacterService

BONUS_ENERGY = 50


class RewardBlitzTeam(ABC):

    def __init__(self, reward_blitz_team: BlitzTeam):
        self.reward_blitz_team = reward_blitz_team

    async def get_blitz_characters(self) -> list[Character]:
        extract_ch = BlitzCharacterService.get_character_from_blitz_character
        return [(await extract_ch(blitz_character)) for blitz_character in self.reward_blitz_team.characters]

    async def reward_blitz(self):
        characters = await self.get_blitz_characters()
        for character in characters:
            await self.reward_blitz_character(character)

    @abstractmethod
    async def reward_blitz_character(self, character: Character):
        raise NotImplementedError


class RewardWinnerBlitzTeam(RewardBlitzTeam):
    def box_type(self):
        return "средний", "medium"

    async def reward_blitz_character(self, character: Character):
        name_box, callback_name_box = self.box_type()
        callback_data = BoxRewardCallback(box_type=callback_name_box).pack()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Open", callback_data=callback_data)]
        ])
        await bot.send_message(character.characters_user_id, f"Вы получили {name_box} лутбокс", reply_markup=markup)
        await RewardSimpleBlitzTeam(self.reward_blitz_team).reward_blitz_character(character)


class RewardPreWinnerBlitzTeam(RewardWinnerBlitzTeam):

    def box_type(self):
        return "меленький", "small"


class RewardSimpleBlitzTeam(RewardBlitzTeam):
    async def reward_blitz_character(self, character: Character):
        text = "Вы получлил бонусные +50 енергии за блиц турнир"
        await CharacterService.edit_character_energy(
            character_id=character.id,
            amount_energy=BONUS_ENERGY,
        )
        await bot.send_message(character.characters_user_id, text)


class BlitzRewardService:
    @staticmethod
    async def reward_blitz_team(reward_blitz_team: RewardBlitzTeam):
        await reward_blitz_team.reward_blitz()
