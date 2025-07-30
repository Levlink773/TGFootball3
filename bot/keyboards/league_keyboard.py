from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from constants_leagues import GetConfig, TypeLeague

from .utils_keyboard import menu_plosha

from ..callbacks.league_callbacks import (
    JoinToFight, 
    ViewCharacterRegisteredInMatch,
    EpizodeDonateEnergyToMatch
)

def menu_best_league(keyboard: ReplyKeyboardBuilder):
    config = GetConfig.get_config(
        type_league=TypeLeague.BEST_LEAGUE
    )
    if config.league_is_active:
        keyboard.button(text = "🏆 Єврокубки")
    

def menu_best_20_club(keyboard: ReplyKeyboardBuilder):
    config = GetConfig.get_config(
        type_league=TypeLeague.TOP_20_CLUB_LEAGUE
    )
    if config.league_is_active:
        keyboard.button(text = "🏆 Національний Кубок України")
    

def menu_new_club(keyboard: ReplyKeyboardBuilder):
    config = GetConfig.get_config(
        type_league=TypeLeague.NEW_CLUB_LEAGUE
    )
    if config.league_is_active:
        keyboard.button(text = "🏆 Ліга нових клубів") 

def menu_default_league(keyboard: ReplyKeyboardBuilder):
    default_config = GetConfig.get_config(
        type_league=TypeLeague.DEFAULT_LEAGUE
    )
    if default_config.league_is_active:
        keyboard.button(text = "🏟 Стадіон - Ліга")


def keyboard_menu_league():
    keyboard = ReplyKeyboardBuilder()
    menu_default_league(keyboard)
    menu_best_league(keyboard)
    menu_best_20_club(keyboard)
    menu_new_club(keyboard)
    keyboard.attach(menu_plosha())
    return keyboard.adjust(1).as_markup()
    
def keyboard_to_join_character_to_fight(match_id: int):
    return (
        InlineKeyboardBuilder()
        .button(text = "⚽️ Приєднатися до матчу!", callback_data=JoinToFight(
            match_id=match_id
        ))
        
        .button(text = "❔ Хто зареєструвався на матч",
                callback_data=ViewCharacterRegisteredInMatch(match_id=match_id))
        .adjust(1)
        .as_markup()
    )
    
def donate_energy_to_match(match_id: str, time_end_goal: int):
    return (
        InlineKeyboardBuilder()
        .button(
            text = "🔱 Підвищити шанс голу",
            callback_data = EpizodeDonateEnergyToMatch(
                match_id      = match_id,
                time_end_goal = time_end_goal
            )
        )
        .as_markup()
    )

    
def menu_league_zone():
    return(ReplyKeyboardBuilder()
           .button(text = "📝 Зареєструватися в матч")
           .button(text = "📋 Таблиця")
        #    .button(text = "🔋 Задонатити в матч")
           .button(text = "📅 Календар ігор")
           .button(text = "📊 Результати")
           .attach(menu_plosha())
           .adjust(1,2,2,1)
           .as_markup(resize_keyboard = True)
           )
    
def menu_beast_league_zone():
    return(ReplyKeyboardBuilder()
           .button(text = "📝 Зареєструватися в матч Єврокубків")
           .button(text = "📋 Таблиця Єврокубків")
        #    .button(text = "🔋 Задонатити в матч")
           .button(text = "📅 Календар Єврокубків")
           .button(text = "📊 Результати Єврокубків")
           .attach(menu_plosha())
           .adjust(1,1,1,2,1)
           .as_markup(resize_keyboard = True)
           )
    
def menu_national_cup_ukraine():
    return(ReplyKeyboardBuilder()
           .button(text = "📝 Зареєструватися в матч Кубка України")
           .button(text = "📋 Таблиця Кубка України")
        #    .button(text = "🔋 Задонатити в матч Кубка України")
           .button(text = "📅 Календар Кубка України")
           .button(text = "📊 Результати Кубка України")
           .attach(menu_plosha())
           .adjust(1,1,1,2,1)
           .as_markup(resize_keyboard = True)
           )
    

def menu_new_club_league():
    return(ReplyKeyboardBuilder()
           .button(text = "📝 Зареєструватися в матч Нових клубів")
           .button(text = "📋 Таблиця Нових клубів")
        #    .button(text = "🔋 Задонатити в матч Нових клубів")
           .button(text = "📅 Календар Нових клубів")
           .button(text = "📊 Результати Нових клубів")
           .attach(menu_plosha())
           .adjust(1,1,1,2,1)
           .as_markup(resize_keyboard = True)
           )