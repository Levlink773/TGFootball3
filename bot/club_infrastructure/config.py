from aiogram.types import FSInputFile

from dataclasses import dataclass
from typing import Dict, Union, List

from constants_leagues import TypeLeague
from best_club_league.types import LeagueRanking

from .types import InfrastructureType, InfrastructureLevel
from .constans import (
    PHOTO_TRAINING_BASE,
    PHOTO_TRAINING_CENTER,
    PHOTO_PREMIUM_FOND,
    PHOTO_STADIUM,
    PHOTO_SPORTS_MEDICINE,
    PHOTO_ACADEMY_TALENT
)

@dataclass(frozen=True)
class InfrastructureBonus:
    bonuses: Dict[InfrastructureLevel, int]

    def get(self, level: InfrastructureLevel) -> int:
        return self.bonuses.get(level, 0)


def create_bonus(*values: int) -> InfrastructureBonus:
    levels = list(InfrastructureLevel)
    return InfrastructureBonus(
        {levels[i]: values[i] for i in range(len(values))}
        )


UPGRADE_COSTS: Dict[InfrastructureLevel, int] = {
    InfrastructureLevel.LEVEL_1: 100,
    InfrastructureLevel.LEVEL_2: 250,
    InfrastructureLevel.LEVEL_3: 500,
    InfrastructureLevel.LEVEL_4: 1000,
    InfrastructureLevel.LEVEL_5: 2000,
}


INFRASTRUCTURE_BONUSES: Dict[InfrastructureType, InfrastructureBonus] = {
    InfrastructureType.TRAINING_BASE: create_bonus(0, 2, 5, 7, 10, 15),
    InfrastructureType.TRAINING_CENTER: create_bonus(0, 5, 10, 15, 20, 30),
    InfrastructureType.PREMIUM_FOND: create_bonus(0, 3, 7, 12, 18, 25),
    InfrastructureType.STADIUM: create_bonus(0, 3, 6, 10, 15, 25),
    InfrastructureType.SPORTS_MEDICINE: create_bonus(0, -2, -5, -8, -12, -20),
    InfrastructureType.ACADEMY_TALENT: create_bonus(0, 2, 4, 7, 10, 15),
}


PHOTOS_INFRASTRUCTURE: Dict[InfrastructureType, FSInputFile] = {
    InfrastructureType.TRAINING_BASE:   PHOTO_TRAINING_BASE,
    InfrastructureType.TRAINING_CENTER: PHOTO_TRAINING_CENTER,
    InfrastructureType.PREMIUM_FOND:    PHOTO_PREMIUM_FOND,
    InfrastructureType.STADIUM:         PHOTO_STADIUM,
    InfrastructureType.SPORTS_MEDICINE: PHOTO_SPORTS_MEDICINE,
    InfrastructureType.ACADEMY_TALENT:  PHOTO_ACADEMY_TALENT,
}


POINTS_FROM_DISTRIBUTE_FROM_LEAGUE: Dict[
    TypeLeague, Union[List[int], Dict[LeagueRanking, List[int]]]
] = {
    TypeLeague.BEST_LEAGUE: {
        LeagueRanking.GROUP_A: [50, 40, 30],
        LeagueRanking.GROUP_B: [40, 30, 20],
        LeagueRanking.GROUP_C: [30, 20, 10]
    },
    TypeLeague.DEFAULT_LEAGUE: [30, 15, 10],
    TypeLeague.TOP_20_CLUB_LEAGUE: [30, 20, 10]
}
