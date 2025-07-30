from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.routers.statistic.callbacks.club_league_callbacks import (
    SelectClubLeagueStatistic,
    ViewClubLeagueStatistic
)
from bot.keyboards.utils_keyboard import pagination_keyboard
from bot.callbacks.switcher import SwitchLeagueClub

from database.models.club import Club

from config import LEAGUES
from constants import ITEM_PER_PAGE

def menu_club_league_statistic():
    keyboard = InlineKeyboardBuilder()
    for league in LEAGUES[::-1]:
        keyboard.button(
            text=league, 
            callback_data=SelectClubLeagueStatistic(
                league=league,
            )
        )
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True) 


def select_club_league_statistic(
    league_clubs: list[Club],
    page: int = 0,
):
    keyboard = InlineKeyboardBuilder()
    
    start = page * ITEM_PER_PAGE
    end = start + ITEM_PER_PAGE    

    keyboard.attach(
        pagination_keyboard(
            total_items  = len(league_clubs), 
            current_page = page, 
            switcher     = SwitchLeagueClub
        )
    )
    for club in league_clubs[start:end]:
        text_club = "⚽ {name_club}".format(
            name_club = club.name_club,
        )
        
        keyboard.button(
            text=text_club, 
            callback_data=ViewClubLeagueStatistic(
                club_id=club.id
            )
        )
    keyboard.adjust(3,*([1]*10))
    return keyboard.as_markup()

