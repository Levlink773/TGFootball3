from aiogram.filters.callback_data import CallbackData


class JoinToFight(CallbackData, prefix="join_to_fight"):
    match_id: str
    
    
class ViewCharacterRegisteredInMatch(CallbackData, prefix = "view_reg_match"):
    match_id: str
    
    
class EpizodeDonateEnergyToMatch(CallbackData, prefix = "donate_energy"):
    match_id: str
    time_end_goal: int