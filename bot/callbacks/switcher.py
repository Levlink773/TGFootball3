from aiogram.filters.callback_data import CallbackData

class Switcher(CallbackData, prefix = "ABC"):
    page: int
    side: str

class SwitchClub(CallbackData, prefix="switch_club"):
    page: int
    side: str

    
class SwitchMyItem(CallbackData, prefix="switch_my_item"):
    page: int
    side: str


class SwitchLeagueClub(CallbackData, prefix="switch_league_club"):
    page: int
    side: str