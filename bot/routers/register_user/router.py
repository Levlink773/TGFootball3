from aiogram import Router
from .routers.create_character import create_character_router
from .routers.join_to_club import join_to_club_router
from .routers.create_club_from_join import create_club_from_join_router
from .routers.join_to_training import first_training_router
from .routers.select_params_character import select_params_create_character_router
from .routers.select_gender import select_gender_router
from .routers.new_member_bonus import bonus_new_member_router
from .routers.open_reward_box import open_box_new_member_router

register_user_router = Router(name="register_user_router")

register_user_router.include_routers(
    create_character_router,
    select_gender_router,
    join_to_club_router,
    create_club_from_join_router,
    first_training_router,
    select_params_create_character_router,
    bonus_new_member_router,
    open_box_new_member_router
)
