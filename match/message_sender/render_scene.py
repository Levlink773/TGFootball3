import re
import random
from typing import Optional, Literal

from database.models.character import Character

from match.entities import MatchData
from match.enum import TypeGoalEvent

from .types import SceneTemplate
from .templates import (
    NO_GOAL_EVENT_SCENES,
    GOAL_EVENT_SCENES
)

POSITION_MAP = {
    "goalkeeper": "Воротар",
    "defender": "Захисник",
    "midfielder": "Півзахисник",
    "attacker": "Нападник"
}

EVENT_SCENES = {
    TypeGoalEvent.NO_GOAL : NO_GOAL_EVENT_SCENES, 
    TypeGoalEvent.GOAL: GOAL_EVENT_SCENES
}


class SceneRenderer:
    
    def __init__(
        self, 
        match_data: MatchData, 
        goal_event: TypeGoalEvent,
        characters_scene: list[Character] = [],  # Список персонажей, участвующих в моменте
        scorer: Optional[Character] = None,     # Игрок, забивший гол
        assistant: Optional[Character] = None, # Игрок, сделавший ассист
    ):
        self.match_data = match_data
        self.scenes = EVENT_SCENES[goal_event]
        self.characters_scene = characters_scene
        self.scorer = scorer
        self.assistant = assistant
        self.custom_mapping = self._map_characters_to_positions()

    def _map_characters_to_positions(self) -> dict[str, Character]:
        """
        Определить роли персонажей и их принадлежность к клубам.
        """
        mapping = {}

        for character in self.characters_scene:
            club, prefix = self._get_club_and_prefix(character)
            if not club:
                continue

            for eng_pos, position in POSITION_MAP.items():
                if character.position == position:
                    mapping[prefix + eng_pos] = character

        if self.scorer:
            mapping["scorer"] = self.scorer
        if self.assistant:
            mapping["assistant"] = self.assistant

        return mapping

    def _get_club_and_prefix(self, character: Character) -> tuple[Optional[object], str]:
        if self.match_data.first_club.is_character_in_club(character):
            return self.match_data.first_club, ""
        elif self.match_data.second_club.is_character_in_club(character):
            return self.match_data.second_club, "enemy_"
        return None, ""

    def get_available_positions(self) -> set[str]:
        return set(self.custom_mapping.keys())

    def select_template(self) -> Optional[SceneTemplate]:
        available = self.get_available_positions()
        valid_templates = [
            tmpl for tmpl in self.scenes
            if all(pos in available for pos in tmpl.required_positions)
        ]
        return random.choice(valid_templates) if valid_templates else None

    def render(self) -> str:
        template = self.select_template()
        if not template:
            return "<i>Момент не відбувся — недостатньо гравців</i>"

        return self._fill_template(template.text)

    def _fill_template(
        self, 
        template_text: str, 
    ) -> str:
        def get_nick(position_key: str) -> str:
            if position_key in self.custom_mapping:
                return self.custom_mapping[position_key].name

            return "<i>Неизвестный игрок</i>"

        return re.sub(r"\{(\w+?)\}", lambda m: get_nick(m.group(1)), template_text)