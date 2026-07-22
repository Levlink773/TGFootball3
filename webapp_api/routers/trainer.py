"""Тренер (QTE) in-app session.

Bot parity: same registration windows (TrainingTimer + 30m register + 30m
session), training-key consumption, 50-player cap, same per-step scoring
(<=3s -> 7 pts, then -2 per 0.3s, floor 2) and the same end-reward ranges.

ponytail: the bot's full trainer session has extra non-QTE stages; the app
session is 10 QTE steps (2 rounds x 5). Session state (step/score/direction)
lives in this process's memory keyed by user_id — single uvicorn worker.
Upgrade path: persist step state to character_join_training.stage.
"""
import secrets
import time
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from aiogram.utils.web_app import WebAppInitData

from training.constans import (
    DIRECTIONS,
    ENERGY_RANGES,
    MAX_LIMIT_JOIN_CHARACTERS,
    MIN_SCORE,
    PENALTY_STEP,
    PENALTY_VALUE,
    STAT_RANGES,
    TIME_REGISTER_TRAINING,
    TIME_TRAINING,
)
from constants import const_name_characteristics
from services.character_service import CharacterService
from services.training_service import TrainingService

from webapp_api.auth import auth_user

trainer_router = APIRouter()

TOTAL_STEPS = 10
BASE_SCORE = 7
FAST_WINDOW_S = 3.0

# user_id -> {step, score, direction, issued_at, done, stat_points, stat_claimed}
_sessions: dict[int, dict] = {}


def _window(timer):
    """(register_open, session_end) for the latest TrainingTimer."""
    start = timer.time_start
    return start, start + TIME_REGISTER_TRAINING + TIME_TRAINING


async def _active_timer():
    timer = await TrainingService.get_last_training_timer()
    if not timer:
        return None
    open_at, end_at = _window(timer)
    if open_at <= datetime.now() < end_at:
        return timer
    return None


def _issue_step(sess):
    sess["direction"] = secrets.choice(DIRECTIONS)
    sess["issued_at"] = time.monotonic()


def _range_value(ranges, score):
    for r, v in ranges.items():
        if score in r:
            return v
    return list(ranges.values())[-1]


@trainer_router.get("/trainer/session")
async def trainer_state(auth: WebAppInitData = Depends(auth_user)):
    timer = await TrainingService.get_last_training_timer()
    now = datetime.now()
    sess = _sessions.get(auth.user.id)
    active = None
    if timer:
        open_at, end_at = _window(timer)
        active = {"open_at": open_at.isoformat(), "end_at": end_at.isoformat(),
                  "is_open": open_at <= now < end_at}
    return {
        "window": active,
        "in_session": bool(sess and not sess["done"]),
        "step": sess["step"] if sess else 0,
        "total_steps": TOTAL_STEPS,
        "score": sess["score"] if sess else 0,
        "direction": sess["direction"] if sess and not sess["done"] else None,
        "directions": DIRECTIONS,
        "done": bool(sess and sess["done"]),
        "stat_points": sess.get("stat_points") if sess else None,
        "stat_claimed": bool(sess and sess.get("stat_claimed")),
    }


@trainer_router.post("/trainer/join")
async def trainer_join(auth: WebAppInitData = Depends(auth_user)):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")

    timer = await _active_timer()
    if not timer:
        raise HTTPException(status_code=409, detail="Зараз немає активної сесії тренера. Сесії: 10:00, 13:00, 19:00")

    open_at, end_at = _window(timer)
    joined = await TrainingService.user_is_join_to_training(
        user_id=auth.user.id, range_training_times=[open_at, end_at]
    )
    if joined:
        # resume: allow re-entering an unfinished in-memory session
        sess = _sessions.get(auth.user.id)
        if sess and not sess["done"]:
            return {"joined": True, "resumed": True, "step": sess["step"], "score": sess["score"],
                    "direction": sess["direction"]}
        raise HTTPException(status_code=409, detail="Ти вже брав участь у цій сесії")

    if (character.training_key or 0) < 1:
        raise HTTPException(status_code=409, detail="Немає ключів тренування")

    others = await TrainingService.get_joined_users([open_at, end_at])
    if len(others) >= MAX_LIMIT_JOIN_CHARACTERS:
        raise HTTPException(status_code=409, detail="Сесія заповнена (50 гравців)")

    await TrainingService.add_character_to_training(character_id=character.id, user_id=auth.user.id)
    await CharacterService.remove_training_key(character_id=character.id)

    sess = {"step": 1, "score": 0, "done": False}
    _issue_step(sess)
    _sessions[auth.user.id] = sess
    return {"joined": True, "resumed": False, "step": 1, "score": 0, "direction": sess["direction"]}


class Answer(BaseModel):
    direction: str


@trainer_router.post("/trainer/answer")
async def trainer_answer(req: Answer, auth: WebAppInitData = Depends(auth_user)):
    sess = _sessions.get(auth.user.id)
    if not sess or sess["done"]:
        raise HTTPException(status_code=409, detail="Немає активної сесії")

    correct = req.direction == sess["direction"]
    points = 0
    if correct:
        elapsed = time.monotonic() - sess["issued_at"]
        if elapsed <= FAST_WINDOW_S:
            points = BASE_SCORE
        else:
            points = max(MIN_SCORE, int(BASE_SCORE - ((elapsed - FAST_WINDOW_S) // PENALTY_STEP) * PENALTY_VALUE))
        sess["score"] += points

    finished = sess["step"] >= TOTAL_STEPS
    if finished:
        sess["done"] = True
        sess["stat_points"] = _range_value(STAT_RANGES, sess["score"])
        energy = _range_value(ENERGY_RANGES, sess["score"])
        sess["energy"] = energy
        character = await CharacterService.get_character(character_user_id=auth.user.id)
        await TrainingService.update_score_user(user_id=auth.user.id, score=sess["score"])
        await TrainingService.end_user_training(user_id=auth.user.id)
        if character:
            await CharacterService.edit_character_energy(character_id=character.id, amount_energy=energy)
    else:
        sess["step"] += 1
        _issue_step(sess)
        await TrainingService.update_score_user(user_id=auth.user.id, score=sess["score"])

    return {
        "correct": correct,
        "points": points,
        "score": sess["score"],
        "step": sess["step"],
        "done": sess["done"],
        "direction": None if sess["done"] else sess["direction"],
        "stat_points": sess.get("stat_points"),
        "energy": sess.get("energy"),
    }


class PickStat(BaseModel):
    stat: str


@trainer_router.post("/trainer/pick-stat")
async def trainer_pick_stat(req: PickStat, auth: WebAppInitData = Depends(auth_user)):
    sess = _sessions.get(auth.user.id)
    if not sess or not sess["done"]:
        raise HTTPException(status_code=409, detail="Сесія ще не завершена")
    if sess.get("stat_claimed"):
        raise HTTPException(status_code=409, detail="Нагороду вже забрано")
    if req.stat not in const_name_characteristics:
        raise HTTPException(status_code=400, detail="Невідома характеристика")

    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")

    sess["stat_claimed"] = True
    await CharacterService.update_character_characteristic(
        character_id=character.id,
        type_characteristic=req.stat,
        amount_add_points=sess["stat_points"],
    )
    result = {"claimed": True, "stat": req.stat, "points": sess["stat_points"]}
    _sessions.pop(auth.user.id, None)
    return result
