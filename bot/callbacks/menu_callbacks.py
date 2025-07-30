from aiogram.filters.callback_data import CallbackData


class NextInstruction(CallbackData, prefix="next_instruction"):
    index_instruction: int