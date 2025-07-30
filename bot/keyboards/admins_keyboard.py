from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks.admins_callbacks import AdminSelectPvpDuel

from database.models.duel import Duel



def select_option_newsletter():
    return (
        InlineKeyboardBuilder()
        .button(text = "По exp", 
                callback_data = "newsletter_exp")
        # .button(text = "По дате регистрации",
        #         callback_data = "newsletter_time_reg")
        .button(text = "По всем пользователям", 
                callback_data = "newsletter_all_users")
        .adjust(1)
        .as_markup()
    )
    
def view_last_pvp_matches(
        matches: list[Duel]
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for match in matches:
        text_winner = "=" if isinstance(match.get_winner_duel, list) else f"[{match.get_winner_duel.name:.5}]"
            
        builder.button(
            text = f"{match.user_1.name:.8} vs {match.user_2.name:.8} ⚔️{text_winner}",
            callback_data = AdminSelectPvpDuel(
                pvp_duel_id = match.duel_id
            )
        )
    builder.adjust(1)
    return builder.as_markup()
        