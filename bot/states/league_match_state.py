from aiogram.filters.state import State, StatesGroup

class DonateEnergyInMatch(StatesGroup):
    send_count_donate_energy    = State()
    send_epizode_donate_energy  = State()