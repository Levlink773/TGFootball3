import random
from typing import Optional, Union

from aiogram import Bot
from aiogram.types import FSInputFile, Message

from bot.keyboards.league_keyboard import donate_energy_to_match
from utils.photo_utils import get_photo, save_photo_id

from database.models.character import Character
from database.models.match_character import MatchCharacter

from match.entities import MatchData, MatchClub
from match.enum import TypeGoalEvent
from match.constans import (
    GOAL_PHOTOS_PATCH, 
    NO_GOAL_PHOTOS_PATCH,
    MVP_PHOTO_PATCH,
    DONATE_ENERGY_PATCH_PHOTOS,
    END_MATCH_PHOTOS_PATCH,
    SEND_INFO_CHARACTERS_PATCH_PHOTOS,
    START_MATCH_PHOTO_PATCH,
    MIN_DONATE_ENERGY_TO_BONUS_KOEF,
    KOEF_DONATE_ENERGY
)

from .templates import (
    GetterTemplatesMatch,
    TemplatesMatch
)
from .render_scene import SceneRenderer

from utils.rate_limitter import rate_limiter

from loader import bot
from logging_config import logger

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
                    photo = photo,
                    character = character,
                    caption = text,
                    keyboard = keyboard
                )
                if message and message.photo and message.photo[0].file_id:
                    message_photo = message
            else:
                await self._send_message(
                    text = text,
                    character = character,
                    keyboard = keyboard
                )
        return message_photo
    
    @rate_limiter
    async def _send_message(
        self,
        text: str,
        character: Character,
        keyboard: Optional[dict] = None,
    ) -> Message:
        try:
            return await self._bot.send_message(
                chat_id = character.characters_user_id,
                text = text,
                reply_markup = keyboard
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
                chat_id = character.characters_user_id,
                caption = caption,
                photo = photo,
                reply_markup = keyboard
            )
        except Exception as E:
            logger.error(
                f"Error sending photo to {character.character_name}: {E}"
            )


class MatchSender:
    sender = Sender()
    
    def __init__(
        self,
        match_data: MatchData,
    ) -> None:
        
        self.match_data = match_data
        self.getter_templates = GetterTemplatesMatch(match_data)

    async def start_match(self) -> None:
        is_save, photo = await get_photo(START_MATCH_PHOTO_PATCH)

        for club in self.match_data.all_clubs:
            text = self.getter_templates.format_message(
                template = TemplatesMatch.START_MATCH,
                extra_context = {
                    'stadium_name': club.stadium_name
                }
            )
            message_photo = await self.sender.send_messages(
                text = text,
                characters = club.club.characters,
                photo = photo
            )
            if message_photo and not is_save:
                await save_photo_id(
                    patch_to_photo = START_MATCH_PHOTO_PATCH,
                    photo_id = message_photo.photo[0].file_id,
                )
    async def send_participants_match(self) -> None:

        def text_participants(characters: list[Character]) -> str:
            if not characters:
                return "На матч не приїхали гравці"
            
            participants = "".join(
                TemplatesMatch.TEMPLATE_PARTICIPANT.value.format(
                    character_name = character.character_name,
                    power_user = character.full_power,
                    lvl = character.level
                )
                for character in characters
            )
            return participants
            
            
        random_patch = get_random_photo(SEND_INFO_CHARACTERS_PATCH_PHOTOS)
        is_save, photo = await get_photo(random_patch)
        text = self.getter_templates.format_message(
            template = TemplatesMatch.TEMPLATE_PARTICIPANTS_MATCH,
            extra_context = {
                "players_first_club": text_participants(
                    characters = self.match_data.first_club.characters_in_match
                ),
                "players_second_club": text_participants(
                    characters = self.match_data.second_club.characters_in_match
                ),
            }
        )
        message_photo = await self.sender.send_messages(
            text = text,
            characters = self.match_data.all_characters,
            photo = photo
        )
        if message_photo and not is_save:
            await save_photo_id(
                patch_to_photo = random_patch,
                photo_id = message_photo.photo[0].file_id,
            )
            
    async def send_event_scene(
        self,
        goal_event: TypeGoalEvent,
        characters_scene: list[Character] = [],
        character_goal: Optional[Character] = None,
        character_assist: Optional[Character] = None,
        goal_club: Optional[MatchClub] = None,
    ) -> None:
        
        render_scene  = SceneRenderer(
            match_data = self.match_data,
            goal_event = goal_event,
            characters_scene = characters_scene,
            scorer = character_goal,
            assistant = character_assist
        )
        patch_to_photo = get_random_patch_photo_by_event(
            event = goal_event
        )
        is_save, photo = await get_photo(patch_to_photo)
        text_scene = render_scene.render()
        if character_goal:
            template_score = TemplatesMatch.TEMPLATE_SCORE
            text_score = self.getter_templates.format_message(
                template = template_score,
                extra_context = {
                    "scoring_club": goal_club.club_name,
                }
            )
            text_scene+= f"{text_score}"
            
        message_photo = await self.sender.send_messages(
            text = text_scene,
            characters = self.match_data.all_characters_in_clubs,
            photo = photo
        )
        if message_photo and not is_save:
            await save_photo_id(
                patch_to_photo = patch_to_photo,
                photo_id = message_photo.photo[0].file_id,
            )
        
    async def send_ping_donate_energy(self, goal_time: int) -> None:
        chance_clubs = self.match_data.get_chance_clubs()
        template = TemplatesMatch.TEMPLATE_COMING_GOAL
        keyboard = donate_energy_to_match(
            match_id = self.match_data.match_id,
            time_end_goal = goal_time,
        )

        random_patch = get_random_photo(DONATE_ENERGY_PATCH_PHOTOS)
        is_save, photo = await get_photo(random_patch)
        text = self.getter_templates.format_message(
            template = template,
            extra_context = {
                "chance_first_club": chance_clubs[0] * 100,
                "chance_second_club": chance_clubs[1] * 100,
                "min_donate_energy_bonus": MIN_DONATE_ENERGY_TO_BONUS_KOEF,
                "koef_donate_energy": KOEF_DONATE_ENERGY*100 
            }
        )
        message_photo = await self.sender.send_messages(
            characters = self.match_data.all_characters_in_clubs,
            text = text,
            keyboard = keyboard,
            photo = photo
        )
        if message_photo and not is_save:
            await save_photo_id(
                patch_to_photo = random_patch,
                photo_id = message_photo.photo[0].file_id,
            )
         
    async def send_end_match(
        self, 
        winner_match_club: Optional[MatchClub] = None    
    ):
        random_patch = get_random_photo(END_MATCH_PHOTOS_PATCH)
        is_save, photo = await get_photo(random_patch)
        
        if winner_match_club:
            loser_club = self.match_data.get_opposite_club(
                club_id = winner_match_club.club_id
            )
            template = TemplatesMatch.TEMPLATE_END
            template_match_info = TemplatesMatch.WIN_LOSE_TEMPLATE
            text_match_info = self.getter_templates.format_message(
                template = template_match_info,
                extra_context = {
                    "winner_club_name": winner_match_club.club_name,
                    "loser_club_name":  loser_club.club_name,
                }
            )
            text = self.getter_templates.format_message(
                template = template,
                extra_context = {
                    "winner_club_name"  : winner_match_club.club_name,
                    "loser_club_name"   : loser_club.club_name,
                    "match_information" : text_match_info
                }
            )
        else:
            template = TemplatesMatch.DRAW_TEMPLATE
            text = self.getter_templates.format_message(template = template)
        
        message_photo = await self.sender.send_messages(
            characters = self.match_data.all_characters_in_clubs,
            text = text,
            photo = photo
        ) 
        if message_photo and not is_save:
            await save_photo_id(
                patch_to_photo = random_patch,
                photo_id = message_photo.photo[0].file_id,
            )
        
    async def send_character_reward(
        self,
        character: Character,
        exp: int,
        money: int
    ) -> None:
        
        template_reward = TemplatesMatch.TEMPLATE_REWARD_CHARACTER
        text = self.getter_templates.format_message(
            template = template_reward,
            extra_context = {
                "exp": exp,
                "money": money
            }
        )
        await self.sender._send_message(
            character = character,
            text = text
        )
        
    async def send_no_characters_in_match(self) -> None:
        template = TemplatesMatch.TEMPLATE_NO_CHARACTERS_IN_MATCH
        text = self.getter_templates.format_message(template = template)
        
        await self.sender.send_messages(
            characters = self.match_data.all_characters_in_clubs,
            text = text
        )    
    
    async def send_congratulation_mvp(
        self,
        first_mvp: Union[MatchCharacter, Character] | None,
        second_mvp: Union[MatchCharacter, Character] | None
    ) -> None:
        
        
        text_mvp_characters = ""
        is_save, photo = await get_photo(MVP_PHOTO_PATCH)

        for mvp in [first_mvp, second_mvp]:
            if not mvp:
                continue
            match_character, character = mvp
            
            template = TemplatesMatch.TEMPLATE_MVP_PLAYER_POINTS
            text_mvp_characters += self.getter_templates.format_message(
                template = template,
                extra_context = {
                    "nickname": character.character_name,
                    "points": match_character.count_score
                }
            )
        template = TemplatesMatch.TEMPLATE_MVP_CONGRATULATION
        text = self.getter_templates.format_message(
            template = template,
            extra_context = {
                "text_mvp_characters":text_mvp_characters or "Немає MVP",
            }
            
        )
        message_photo = await self.sender.send_messages(
            characters = self.match_data.all_characters_in_clubs,
            text = text,
            photo = photo
        )
    
        if message_photo and not is_save:
            await save_photo_id(
                patch_to_photo = MVP_PHOTO_PATCH,
                photo_id = message_photo.photo[0].file_id,
            )
    
    
def get_random_patch_photo_by_event(event: TypeGoalEvent) -> FSInputFile|str:
    photos_event = {
        TypeGoalEvent.GOAL: GOAL_PHOTOS_PATCH,
        TypeGoalEvent.NO_GOAL: NO_GOAL_PHOTOS_PATCH,
    }

    return random.choice(photos_event[event])

def get_random_photo(patch_photos: list[str]) -> str:
    return random.choice(patch_photos)