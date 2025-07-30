import random

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.training.callbacks.training_callbacks import (
    JoinToTraining, 
    NextStage
)

from training.constans import MAX_LIMIT_JOIN_CHARACTERS
from training.types import Stage


def keyboard_join_training(
    count_users: int,
    end_time_health: int,
):
    text = "Приєднатися до тренування [{count_users}/{max_limit}]".format(
        count_users = count_users,
        max_limit = MAX_LIMIT_JOIN_CHARACTERS
    )
    
    return (
        InlineKeyboardBuilder()
        .button(text = text,
                callback_data = JoinToTraining(
                    end_time_health = end_time_health,
                )
        )
        .adjust(1)
        .as_markup()
    )
    
    
def next_stage_keyboard(
    current_stage: Stage,
    end_time_health: int
):
    keyboard = InlineKeyboardBuilder()
    positive_points = random.sample(range(1, 6), 2)
    negative_point = random.choice(range(-5, 0))
    random_points = positive_points + [negative_point]
    random.shuffle(random_points)
    emoji_points = dict(zip(["1️⃣", "2️⃣", "3️⃣"], random_points))

    for emj, score in emoji_points.items():
        keyboard.button(
            text=emj,
            callback_data=NextStage(
                next_stage=current_stage.next_stage(),
                count_score=score,
                end_time_health = end_time_health
            )
        )
    return keyboard.as_markup()