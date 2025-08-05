import random
from typing import Optional

from aiogram import Bot
from aiogram.types import FSInputFile, Message

from bot.keyboards.blitz_keyboard import donate_energy_to_blitz_match
from database.models.character import Character
from loader import bot
from logging_config import logger
from utils.blitz_photo_utils import get_photo, save_photo_id
from utils.rate_limitter import rate_limiter
from .render_scene import SceneRenderer
from .templates import (
    GetterTemplatesMatch,
    TemplatesMatch
)
from ..constans import (
    GOAL_PHOTOS_PATCH,
    NO_GOAL_PHOTOS_PATCH,
    DONATE_ENERGY_PATCH_PHOTOS,
    END_MATCH_PHOTOS_PATCH,
    SEND_INFO_CHARACTERS_PATCH_PHOTOS,
    START_MATCH_PHOTO_PATCH,
    MIN_DONATE_ENERGY_TO_BONUS_KOEF,
    KOEF_DONATE_ENERGY, STAGE_MAP
)
from ..entities import BlitzMatchData, MatchTeamBlitz
from ..enum_blitz_match import TypeGoalEvent


class Sender:
    _bot: Bot = bot

    async def send_messages(
            self,
            text: str,
            characters: list[Character],
            photo: Optional[str | FSInputFile] = None,
            keyboard: Optional[dict] = None,
    ) -> Message:
        message_photo = None
        for character in characters:
            if character.is_bot:
                continue

            if photo:
                message: Message = await self._send_photo(
                    photo=photo,
                    character=character,
                    caption=text,
                    keyboard=keyboard
                )
                if message and message.photo and message.photo[0].file_id:
                    message_photo = message
            else:
                await self._send_message(
                    text=text,
                    character=character,
                    keyboard=keyboard
                )
        return message_photo

    @rate_limiter
    async def _send_message(
            self,
            text: str,
            character: Character,
            keyboard: Optional[dict] = None,
    ) -> Message | None:
        try:
            return await self._bot.send_message(
                chat_id=character.characters_user_id,
                text=text,
                reply_markup=keyboard
            )
        except Exception as E:
            logger.error(
                f"Error sending message to {character.character_name}: {E}"
            )

    @rate_limiter
    async def _send_photo(
            self,
            character: Character,
            caption: str,
            photo: str | FSInputFile,
            keyboard: Optional[dict] = None,
    ) -> Message:
        try:
            return await self._bot.send_photo(
                chat_id=character.characters_user_id,
                caption=caption,
                photo=photo,
                reply_markup=keyboard
            )
        except Exception as E:
            logger.error(
                f"Error sending photo to {character.character_name}: {E}"
            )


class BlitzMatchSender:
    sender = Sender()

    def __init__(
            self,
            match_data: BlitzMatchData,
    ) -> None:
        self.match_data = match_data
        self.getter_templates = GetterTemplatesMatch(match_data)

    async def start_match(self) -> None:
        is_save, photo = await get_photo(START_MATCH_PHOTO_PATCH)

        text = self.getter_templates.format_message(
            template=TemplatesMatch.START_MATCH_FINAL if self.match_data.stage == 1 else TemplatesMatch.START_MATCH,
            extra_context={
                "stages_of_blitz": STAGE_MAP.get(self.match_data.stage / 2)
            }
        )
        message_photo = await self.sender.send_messages(
            text=text,
            characters=self.match_data.all_characters,
            photo=photo
        )
        if message_photo and not is_save:
            await save_photo_id(
                patch_to_photo=START_MATCH_PHOTO_PATCH,
                photo_id=message_photo.photo[0].file_id,
            )

    async def send_participants_match(self) -> None:
        def text_participants(characters: list[Character]) -> str:
            if not characters:
                return "На матч не приїхали гравці"

            participants = "".join(
                TemplatesMatch.TEMPLATE_PARTICIPANT.value.format(
                    character_name=character.character_name,
                    power_user=character.full_power,
                    lvl=character.level
                )
                for character in characters
            )
            return participants

        random_patch = get_random_photo(SEND_INFO_CHARACTERS_PATCH_PHOTOS)
        is_save, photo = await get_photo(random_patch)
        text = self.getter_templates.format_message(
            template=TemplatesMatch.TEMPLATE_PARTICIPANTS_MATCH_FINAL if self.match_data.stage == 1 else TemplatesMatch.TEMPLATE_PARTICIPANTS_MATCH,
            extra_context={
                "players_first_team": text_participants(
                    characters=self.match_data.first_team.characters_in_match
                ),
                "players_second_team": text_participants(
                    characters=self.match_data.second_team.characters_in_match
                ),
            }
        )
        message_photo = await self.sender.send_messages(
            text=text,
            characters=self.match_data.all_characters,
            photo=photo
        )
        if message_photo and not is_save:
            await save_photo_id(
                patch_to_photo=random_patch,
                photo_id=message_photo.photo[0].file_id,
            )

    async def send_event_scene(
            self,
            goal_event: TypeGoalEvent,
            characters_scene: list[Character] = [],
            character_goal: Optional[Character] = None,
            character_assist: Optional[Character] = None,
            character_enemy: Optional[Character] = None,
            goal_team: Optional[MatchTeamBlitz] = None,
    ) -> None:
        render_scene = SceneRenderer(
            match_data=self.match_data,
            goal_event=goal_event,
            characters_scene=characters_scene,
            scorer=character_goal,
            assistant=character_assist,
            character_enemy=character_enemy
        )

        patch_to_photo = get_random_patch_photo_by_event(
            event=goal_event
        )
        is_save, photo = await get_photo(patch_to_photo)
        text_scene = render_scene.render()
        if character_goal:
            template_score = TemplatesMatch.TEMPLATE_SCORE
            text_score = self.getter_templates.format_message(
                template=template_score,
                extra_context={
                    "scoring_team": goal_team.team_name,
                }
            )
            text_scene += f"{text_score}"

        message_photo = await self.sender.send_messages(
            text=text_scene,
            characters=self.match_data.all_characters,
            photo=photo
        )
        if message_photo and not is_save:
            await save_photo_id(
                patch_to_photo=patch_to_photo,
                photo_id=message_photo.photo[0].file_id,
            )

    async def send_ping_donate_energy(self, goal_time: int) -> None:
        chance_teams = self.match_data.get_chance_teams()
        template = TemplatesMatch.TEMPLATE_COMING_GOAL
        keyboard = donate_energy_to_blitz_match(
            blitz_match_id=self.match_data.blitz_match_id,
            time_end_goal=goal_time,
        )

        random_patch = get_random_photo(DONATE_ENERGY_PATCH_PHOTOS)
        is_save, photo = await get_photo(random_patch)
        text = self.getter_templates.format_message(
            template=template,
            extra_context={
                "chance_first_team": chance_teams[0] * 100,
                "chance_second_team": chance_teams[1] * 100,
                "min_donate_energy_bonus": MIN_DONATE_ENERGY_TO_BONUS_KOEF,
                "koef_donate_energy": KOEF_DONATE_ENERGY * 100
            }
        )
        message_photo = await self.sender.send_messages(
            characters=self.match_data.all_characters,
            text=text,
            keyboard=keyboard,
            photo=photo
        )
        if message_photo and not is_save:
            await save_photo_id(
                patch_to_photo=random_patch,
                photo_id=message_photo.photo[0].file_id,
            )

    async def send_end_match(
            self,
            winner_match_team: Optional[MatchTeamBlitz] = None,
            required_consider_power: bool = False,
    ):
        random_patch = get_random_photo(END_MATCH_PHOTOS_PATCH)
        is_save, photo = await get_photo(random_patch)

        if winner_match_team:
            loser_team = self.match_data.get_opposite_team(
                team_id=winner_match_team.team_id
            )
            template = TemplatesMatch.TEMPLATE_END if not required_consider_power else TemplatesMatch.TEMPLATE_END_CONSIDER_POWER
            template_final = TemplatesMatch.TEMPLATE_END_FINAL if not required_consider_power else TemplatesMatch.TEMPLATE_END_CONSIDER_POWER_FINAL
            template = template_final if self.match_data.stage == 1 else template
            template_match_info = TemplatesMatch.WIN_LOSE_TEMPLATE
            text_match_info = self.getter_templates.format_message(
                template=template_match_info,
                extra_context={
                    "winner_team_name": winner_match_team.team_name,
                    "loser_team_name": loser_team.team_name,
                }
            )
            text = self.getter_templates.format_message(
                template=template,
                extra_context={
                    "winner_team_name": winner_match_team.team_name,
                    "loser_team_name": loser_team.team_name,
                    "match_information": text_match_info,
                    "stages_of_blitz": STAGE_MAP.get(self.match_data.stage / 2),
                }
            )
        else:
            template = TemplatesMatch.DRAW_TEMPLATE
            text = self.getter_templates.format_message(template=template)

        message_photo = await self.sender.send_messages(
            characters=self.match_data.all_characters,
            text=text,
            photo=photo
        )
        if message_photo and not is_save:
            await save_photo_id(
                patch_to_photo=random_patch,
                photo_id=message_photo.photo[0].file_id,
            )


def get_random_patch_photo_by_event(event: TypeGoalEvent) -> FSInputFile | str:
    photos_event = {
        TypeGoalEvent.GOAL: GOAL_PHOTOS_PATCH,
        TypeGoalEvent.NO_GOAL: NO_GOAL_PHOTOS_PATCH,
    }

    return random.choice(photos_event[event])


def get_random_photo(patch_photos: list[str]) -> str:
    return random.choice(patch_photos)
