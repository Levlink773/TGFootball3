from aiogram.filters.callback_data import CallbackData

class SelectClubLeagueStatistic(CallbackData, prefix="select_gender"):
    league: str
    

class ViewClubLeagueStatistic(CallbackData, prefix="view_club_league_statistic"):
    club_id: int
