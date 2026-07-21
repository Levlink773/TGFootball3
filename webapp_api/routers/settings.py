from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import update
from aiogram.utils.web_app import WebAppInitData

from database.models.user_bot import UserBot
from database.session import get_session
from services.user_service import UserService

from webapp_api.auth import auth_user

settings_router = APIRouter()


class SettingsUpdate(BaseModel):
    bot_buttons_enabled: bool


@settings_router.get("/settings")
async def get_settings(auth: WebAppInitData = Depends(auth_user)):
    user = await UserService.get_user(user_id=auth.user.id)
    if not user:
        raise HTTPException(status_code=404, detail="No user")
    return {"bot_buttons_enabled": bool(user.bot_buttons_enabled)}


@settings_router.post("/settings")
async def update_settings(req: SettingsUpdate, auth: WebAppInitData = Depends(auth_user)):
    user = await UserService.get_user(user_id=auth.user.id)
    if not user:
        raise HTTPException(status_code=404, detail="No user")
    async for session in get_session():
        async with session.begin():
            await session.execute(
                update(UserBot)
                .where(UserBot.user_id == auth.user.id)
                .values(bot_buttons_enabled=req.bot_buttons_enabled)
            )
    return {"bot_buttons_enabled": req.bot_buttons_enabled}
