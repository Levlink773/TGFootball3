"""Character creation, in the Mini App instead of the bot chat.

Replaces the reply-keyboard FSM at bot/routers/register_user/ (name -> gender ->
position -> confirm, one Telegram message per step). Field-for-field parity with
that flow is the point: any divergence here creates two classes of player.

Callers may not have a `users` row at all — someone who opens the Mini App from
the menu button has never sent the bot a message, so the middleware that creates
it (bot/middlewares/handlers.py) never ran. Both `characters.characters_user_id`
and `clubs.owner_id` are FKs to `users.user_id`, so creating that row first is a
hard precondition, not a courtesy.
"""
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from aiogram.utils.web_app import WebAppInitData
from sqlalchemy.exc import IntegrityError

from config import Gender, PositionCharacter
from const_character import CREATE_CHARACTER_CONST
from database.models.character import Character
from database.models.user_bot import STATUS_USER_REGISTER
from services.character_service import CharacterService
from services.reminder_character_service import RemniderCharacterService
from services.user_service import UserService

from webapp_api.auth import auth_user
from webapp_api.routers.player import player_payload

character_router = APIRouter()

NAME_MIN, NAME_MAX = 2, 20
# Letters (any script), digits, space, hyphen, apostrophe, dot. Rejects emoji,
# zero-width joiners and control characters — and makes an explicit `<`/`>` check
# redundant, which matters because character.name is interpolated into
# parse_mode=HTML broadcasts sent to other players.
NAME_RE = re.compile(r"[\w \-'.]+")


def _clean_name(raw: str) -> str:
    name = re.sub(r"\s+", " ", (raw or "")).strip()
    if not (NAME_MIN <= len(name) <= NAME_MAX):
        raise HTTPException(status_code=400, detail=f"Ім'я: від {NAME_MIN} до {NAME_MAX} символів")
    if not NAME_RE.fullmatch(name):
        raise HTTPException(status_code=400, detail="Ім'я може містити лише літери, цифри, пробіл, дефіс і апостроф")
    return name


async def _ensure_user(auth: WebAppInitData):
    """Get-or-create the users row. Mirrors bot/middlewares/handlers.py:18-23."""
    user = await UserService.get_user(user_id=auth.user.id)
    if user:
        return user
    full_name = " ".join(filter(None, [auth.user.first_name, auth.user.last_name]))
    try:
        await UserService.create_user(
            user_id=auth.user.id,
            user_name=auth.user.username,
            user_full_name=full_name or None,
        )
    except IntegrityError:
        # users.user_id is unique; two concurrent first-launch requests can both
        # miss the SELECT above. The loser just re-reads the winner's row.
        pass
    user = await UserService.get_user(user_id=auth.user.id)
    if not user:
        raise HTTPException(status_code=500, detail="Не вдалося створити профіль")
    return user


class CreateCharacterReq(BaseModel):
    name: str
    gender: str    # Gender member name: "MAN" | "WOMAN"
    position: str  # PositionCharacter member name: "GOALKEEPER" | "DEFENDER" | ...


@character_router.get("/character/options")
async def character_options(auth: WebAppInitData = Depends(auth_user)):
    """Genders and positions with their starting stats, derived from the same
    constants the bot uses — so the wizard can't drift from const_character.py."""
    positions = []
    for position in PositionCharacter:
        base = CREATE_CHARACTER_CONST(position)
        positions.append({
            "key": position.name,
            "label": position.value,
            "stats": {
                "technique": base.technique,
                "kicks": base.kicks,
                "ball_selection": base.ball_selection,
                "speed": base.speed,
                "endurance": base.endurance,
            },
        })
    return {
        "genders": [{"key": g.name, "label": g.value} for g in Gender],
        "positions": positions,
        "name_min": NAME_MIN,
        "name_max": NAME_MAX,
    }


@character_router.post("/character")
async def create_character(req: CreateCharacterReq, auth: WebAppInitData = Depends(auth_user)):
    # Deliberately 200-with-created:false rather than 409. A double tap, a retry
    # after the client's 20s abort, and "already registered through the old bot
    # FSM" are the same situation, and the right answer to all three is "you have
    # a player, carry on" — a 409 would put an error toast in front of a working
    # game. An existing character is never mutated here.
    existing = await CharacterService.get_character(character_user_id=auth.user.id)
    if existing:
        await UserService.edit_status_register(
            user_id=auth.user.id, status=STATUS_USER_REGISTER.END_TRAINING
        )
        return {"created": False, "player": player_payload(existing, auth.user.id)}

    name = _clean_name(req.name)
    try:
        gender = Gender[req.gender]
        position = PositionCharacter[req.position]
    except KeyError:
        raise HTTPException(status_code=400, detail="Невідома стать або позиція")

    user = await _ensure_user(auth)
    base = CREATE_CHARACTER_CONST(position)

    character_obj = Character(
        current_energy=150,
        characters_user_id=user.user_id,
        name=name,
        technique=base.technique,
        kicks=base.kicks,
        ball_selection=base.ball_selection,
        speed=base.speed,
        endurance=base.endurance,
        position=position,   # enum member, not .value — see below
        gender=gender,
        club_id=None,
        is_bot=False,
        referal_user_id=user.referal_user_id,
    )
    try:
        # create_character converts .gender/.position to their .value in place and
        # its get-or-create branch returns a DIFFERENT object, so nothing below may
        # read fields off character_obj. Re-read instead, exactly as the bot does.
        await CharacterService.create_character(character_obj=character_obj)
    except IntegrityError:
        pass  # lost a concurrent create race; the re-read below picks up the winner

    character = await CharacterService.get_character(character_user_id=user.user_id)
    if not character:
        raise HTTPException(status_code=500, detail="Не вдалося створити гравця")

    # reminder_characters.character_id is unique — an unguarded second insert raises.
    if not character.reminder:
        try:
            await RemniderCharacterService.create_character_reminder(character_id=character.id)
        except IntegrityError:
            pass

    # Must happen at creation, not at tutorial completion: every bot button is
    # prefixed 🔒 until END_TRAINING (bot/keyboards/menu_keyboard.py) and the
    # chat flow that used to clear it no longer exists. The tutorial's own
    # "has the player seen the slides" bit is users.tutorial_completed_at.
    await UserService.edit_status_register(
        user_id=user.user_id, status=STATUS_USER_REGISTER.END_TRAINING
    )

    return {"created": True, "player": player_payload(character, user.user_id)}
