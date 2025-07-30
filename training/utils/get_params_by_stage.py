import random
import json
import aiofiles
from typing import Optional

from training.types import (
    Stage,
    TextParamsTraning
)


class GetParams:
    default_patch: str = "training/text/{stage}.json"    
    
    @staticmethod
    async def get_params_epizode(stage: Stage) -> TextParamsTraning:
        patch = GetParams.default_patch.format(stage=stage.value)
        async with aiofiles.open( file= patch, mode='r', encoding='utf-8') as f:
            data = await f.read()
            data: dict = json.loads(data)
            data = random.choice(data)
            
            text_epizode: str = data['text_stage']
            text_coach: str = data['text_coach']
            variable_answers: list[str] = data['variable_answers']
            patch_to_photo: Optional[str] = data.get('patch_to_photo', None)
            
            random.shuffle(variable_answers)
            
            return TextParamsTraning(
                text_epizode=text_epizode,
                text_coach = text_coach,
                variable_answers=variable_answers,
                patch_to_photo=patch_to_photo
            )