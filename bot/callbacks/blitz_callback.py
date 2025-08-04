from aiogram.filters.callback_data import CallbackData


class BlitzRegisterCallback(CallbackData, prefix="blitz_register"):
    blitz_id: int
    max_characters: int


class EpizodeDonateEnergyToBlitzMatch(CallbackData, prefix="donate_energy_to_blitz_match"):
    blitz_match_id: str
    time_end_goal: int


class BoxRewardCallback(CallbackData, prefix="reward_blitz_box"):
    box_type: str
