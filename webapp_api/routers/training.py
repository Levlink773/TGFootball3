from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from aiogram.utils.web_app import WebAppInitData

from services.character_service import CharacterService
from services.training_service import TrainingService

from webapp_api.auth import auth_user

training_router = APIRouter()


@training_router.get("/training")
async def get_training(auth: WebAppInitData = Depends(auth_user)):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")

    reminder = character.reminder
    now = datetime.now()

    training = None
    if reminder and reminder.character_in_training and reminder.time_start_training:
        ends_at = reminder.time_start_training + timedelta(
            seconds=reminder.time_training_seconds or 0
        )
        training = {
            "stats": reminder.training_stats,
            "started_at": reminder.time_start_training.isoformat(),
            "ends_at": ends_at.isoformat(),
            "seconds_left": max(0, int((ends_at - now).total_seconds())),
        }

    education = None
    if reminder:
        can_claim = now > reminder.education_reward_date
        education = {
            "can_claim": can_claim,
            "next_claim_at": reminder.education_reward_date.isoformat(),
            "seconds_left": 0 if can_claim else int(
                (reminder.education_reward_date - now).total_seconds()
            ),
        }

    # Trainer (QTE) session today: joined rows for [00:00, +1d)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    joined_today = await TrainingService.get_joined_users([day_start, day_start + timedelta(days=1)])
    mine = [j for j in joined_today if j.user_id == auth.user.id]
    last_timer = await TrainingService.get_last_training_timer()

    return {
        "energy": character.current_energy,
        "training_keys": character.training_key,
        "in_training": bool(reminder and reminder.character_in_training),
        "training": training,
        "education": education,
        "trainer": {
            "last_session_at": last_timer.time_start.isoformat() if last_timer else None,
            "joined_today": bool(mine),
            "today_score": max((j.scores or 0) for j in mine) if mine else 0,
            "session_ended": all(j.training_is_end for j in mine) if mine else False,
        },
    }
