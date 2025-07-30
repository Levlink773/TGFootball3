from aiogram import Router
from .commands.router import commands_router
from .character.router import character_router
from .gym.router import gym_main_router
from .club.router import club_router
from .league.router import league_main_router
from .stores.router import magazine_main_router
from .hall_fame.router import hall_fame_main_router
from .pvp_duels.router import duel_main_router
from .communication.router import communication_main_router
from .commands.admins_functional.newsletter import admin_newsletter_commands
from .commands.admins_functional.info_new_members import admin_info_new_member_router
from .сhristmas_tree.router import christmas_tree_router
from .statistic.router import statistic_router
from bot.training.routers.answer_stage import answer_etap_router
from bot.training.routers.joined_in_training import join_trainig_router
from bot.training.routers.qte_stage import qte_router
from bot.training.routers.end_training import end_training_router
from bot.training.routers.buy_training_key import buy_training_key_router
from bot.training.routers.duel_stage import training_duel_router
from bot.routers.register_user.router import register_user_router
from bot.club_infrastructure.router_infrastructure import router_infrastructure
from .commands.block_users import block_uses_router

main_router = Router()
main_router.include_routers(
    block_uses_router,
    commands_router,
    register_user_router,
    character_router,
    gym_main_router,
    club_router,
    league_main_router,
    magazine_main_router,
    duel_main_router,
    hall_fame_main_router,
    communication_main_router,
    admin_newsletter_commands,
    admin_info_new_member_router,
    christmas_tree_router,
    join_trainig_router,
    router_infrastructure,
    answer_etap_router,
    qte_router,
    end_training_router,
    buy_training_key_router,
    training_duel_router,
    statistic_router
)
