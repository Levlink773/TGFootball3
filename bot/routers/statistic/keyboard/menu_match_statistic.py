from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from constants_leagues import NAMES_LEAGUES

from league_20_power_club.types import LeagueBestClubRanking

from ..callbacks.match_statistic_callbacks import (
    SelectTypeMatchLeague,
    StatisticsMatches,
    SelectTypeMatchTop20League
)
        
def select_type_league_matches():
    builder = InlineKeyboardBuilder()
    
    for type_league, name_league in NAMES_LEAGUES.items():
        builder.button(
            text=name_league,
            callback_data=SelectTypeMatchLeague(
                type_league=type_league
            )
        )

    builder.adjust(1)
    return builder.as_markup()

def back_to_nenu():
    return (
        InlineKeyboardBuilder()
        .button(
            text="⬅️ Назад",
            callback_data="back_to_menu_select_statistic_matches"
        )
    )


def select_type_matches_best_league():
    return (
        InlineKeyboardBuilder()
        .button(
            text=LeagueBestClubRanking.GROUP_A.value,
            callback_data=SelectTypeMatchTop20League(
                type_group=LeagueBestClubRanking.GROUP_A.value
            )
        )
        .button(
            text=LeagueBestClubRanking.GROUP_B.value,
            callback_data=SelectTypeMatchTop20League(
                type_group=LeagueBestClubRanking.GROUP_B.value
            )
        )
        .button(
            text="🧧 Останній матч",
            callback_data=SelectTypeMatchTop20League(
                type_group="LAST_MATCH"
            )
        )
        .adjust(2,1)
        .attach(back_to_nenu())
        .as_markup()
    )


def select_group(
        ids_groups: list[int],
        my_group_id: int | None             
    ):
    builder = InlineKeyboardBuilder()
    
    for num, id_group in enumerate(ids_groups, start=1):
        text = f"Группа №{num}"
        if id_group == my_group_id:
            text = f"⚽️ {text}"
        builder.button(
            text = text,
            callback_data=StatisticsMatches(
                group_id=id_group
            )
        )
    builder.adjust(2)
    builder.attach(back_to_nenu())

    return builder.as_markup()
