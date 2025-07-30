from pydantic import BaseModel
from typing import Optional
from enum import Enum

from aiogram.types import FSInputFile


class Stage(str, Enum):
    STAGE_1 = "stage_1"
    STAGE_2 = "stage_2"
    STAGE_3 = "stage_3"
    STAGE_4 = "stage_4"
    STAGE_5 = "stage_5"
    STAGE_6 = "stage_6"
    STAGE_7 = "stage_7"
    STAGE_DUEL = "stage_DUEL"
    END_TRAINIG = "end_stage"
    
    def next_stage(self) -> "Stage":
        etaps = list(Stage)
        return etaps[etaps.index(self) + 1]
        
    
class TextParamsTraning(BaseModel):
    text_epizode: str
    text_coach: str
    variable_answers: list[str]
    
    patch_to_photo: Optional[str] = None
    
    @property
    def photo(self) -> Optional[FSInputFile]:
        if not self.patch_to_photo:
            return None
        return FSInputFile(self.patch_to_photo)
    
    @property
    def first_answer_сhoice(self) -> str:
        return self.variable_answers[0]
    
    @property
    def second_answer_сhoice(self) -> str:
        return self.variable_answers[1]
    
    @property
    def third_answer_сhoice(self) -> str:
        return self.variable_answers[2]