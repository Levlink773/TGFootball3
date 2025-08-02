from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks.blitz_callback import EpizodeDonateEnergyToBlitzMatch


def donate_energy_to_blitz_match(blitz_match_id: str, time_end_goal: int):
    return (
        InlineKeyboardBuilder()
        .button(
            text="🔱 Підвищити шанс голу",
            callback_data=EpizodeDonateEnergyToBlitzMatch(
                blitz_match_id=blitz_match_id,
                time_end_goal=time_end_goal
            )
        )
        .as_markup()
    )
