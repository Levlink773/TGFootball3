"""In-app tutorial completion — replaces the bot-chat education gauntlet.

POST /api/tutorial/complete marks the user's bot education finished
(END_TRAINING) so no chat button stays locked. Idempotent. Also backfills
a missing ReminderCharacter row (known strand: education handlers dereference
character.reminder unguarded).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from aiogram.utils.web_app import WebAppInitData

from database.models.user_bot import UserBot, STATUS_USER_REGISTER
from database.models.reminder_character import ReminderCharacter
from database.session import get_session
from services.character_service import CharacterService
from services.user_service import UserService

from webapp_api.auth import auth_user

tutorial_router = APIRouter()


@tutorial_router.get("/tutorial")
async def get_tutorial(auth: WebAppInitData = Depends(auth_user)):
    user = await UserService.get_user(user_id=auth.user.id)
    if not user:
        raise HTTPException(status_code=404, detail="No user")
    return {"completed": user.end_register}


@tutorial_router.post("/tutorial/complete")
async def complete_tutorial(auth: WebAppInitData = Depends(auth_user)):
    user = await UserService.get_user(user_id=auth.user.id)
    if not user:
        raise HTTPException(status_code=404, detail="No user")

    character = await CharacterService.get_character(character_user_id=auth.user.id)
    async for session in get_session():
        async with session.begin():
            if not user.end_register:
                await session.execute(
                    update(UserBot)
                    .where(UserBot.user_id == auth.user.id)
                    .values(status_register=STATUS_USER_REGISTER.END_TRAINING)
                )
            if character:
                has_reminder = await session.scalar(
                    select(ReminderCharacter.id).where(ReminderCharacter.character_id == character.id)
                )
                if not has_reminder:
                    session.add(ReminderCharacter(character_id=character.id))
    return {"completed": True}
