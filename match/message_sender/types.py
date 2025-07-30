from typing import Literal
from dataclasses import dataclass

@dataclass
class SceneTemplate:
    text: str
    required_positions: list[
        Literal[
            "goalkeeper",
            "defender",
            "midfielder",
            "striker"
        ]
    ]