from aiogram.filters.callback_data import CallbackData

class SelectClubLeagueStatistic(CallbackData, prefix="club_league_stat"):
    league: str
    

class ViewClubLeagueStatistic(CallbackData, prefix="view_club_league_statistic"):
    club_id: int
