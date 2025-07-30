from typing import Literal
from aiogram.filters.callback_data import CallbackData

from constants_leagues import TypeLeague

class SelectTypeMatchLeague(CallbackData, prefix="select_type_league_match"):
    type_league: TypeLeague

class SelectTypeMatchTop20League(CallbackData, prefix="select_type_league_match_top20"):
    type_group: Literal[
        "ГРУППА A",
        "ГРУППА B",
        "LAST_MATCH"
    ]

class StatisticsMatches(CallbackData, prefix="select_group_id"):
    group_id: int | str
