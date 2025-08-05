from abc import ABC, abstractmethod

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from blitz.blitz_match.constans import SMALL_BOX_BLITZ_PHOTO, MEDIUM_BOX_BLITZ_PHOTO
from blitz.services.blitz_character_service import BlitzCharacterService
from blitz.services.message_sender.blitz_sender import send_message
from bot.callbacks.blitz_callback import BoxRewardCallback
from database.models.blitz_team import BlitzTeam
from database.models.character import Character
from loader import bot
from services.character_service import CharacterService
from utils.blitz_photo_utils import get_photo, save_photo_id

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
        return "середній", "medium", MEDIUM_BOX_BLITZ_PHOTO

    async def reward_blitz_character(self, character: Character):
        name_box, callback_name_box, photo_path = self.box_type()
        callback_data = BoxRewardCallback(box_type=callback_name_box).pack()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Відкрити 🗝️", callback_data=callback_data)]
        ])

        # Новий український, драйвовий текст з HTML-підсвіткою
        is_save, photo = await get_photo(photo_path)
        msg = await bot.send_photo(
            character.characters_user_id,
            photo=photo,
            caption=f"🎁 <b>Увага!</b> Ви отримали <b>{name_box} лутбокс</b> за блиц-турнір! "
            "Відкрийте його, щоб дізнатися свою нагороду та зарядитися мотивацією! 💥",
            reply_markup=markup,
            parse_mode="HTML"
        )
        # Додаємо +50 енергії всім учасникам команди
        await RewardSimpleBlitzTeam(self.reward_blitz_team).reward_blitz_character(character)
        if msg and not is_save:
            await save_photo_id(
                patch_to_photo=photo_path,
                photo_id=msg.photo[0].file_id,
            )




class RewardPreWinnerBlitzTeam(RewardWinnerBlitzTeam):

    def box_type(self):
        return "меленький", "small", SMALL_BOX_BLITZ_PHOTO


class RewardSimpleBlitzTeam(RewardBlitzTeam):
    async def reward_blitz_character(self, character: Character):
        # Збільшуємо енергію
        await CharacterService.edit_character_energy(
            character_id=character.id,
            amount_energy=BONUS_ENERGY,
        )
        # Епічний фініш повідомлення про енергію
        await send_message(
            character=character,
            text="⚡ <b>+50 енергії</b> за участь у блиц-турнірі! Дякуємо, що були з нами — "
            "поповнюйте запаси та повертайтесь до наступних батлів! 💪",
        )


class BlitzRewardService:
    @staticmethod
    async def reward_blitz_team(reward_blitz_team: RewardBlitzTeam):
        await reward_blitz_team.reward_blitz()
