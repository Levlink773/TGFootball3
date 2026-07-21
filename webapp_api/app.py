"""TG Football Mini App API — sidecar FastAPI service (port 3004).

Reads the same MySQL as the bot via the bot's own services/models.
Run: uvicorn webapp_api.app:app --host 127.0.0.1 --port 3004
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.base_acces import get_base
get_base()  # register ALL models so string-name relationships resolve

from webapp_api.routers.player import player_router
from webapp_api.routers.leagues import leagues_router
from webapp_api.routers.matches import matches_router
from webapp_api.routers.hall_of_fame import hall_of_fame_router
from webapp_api.routers.training import training_router
from webapp_api.routers.shop import shop_router
from webapp_api.routers.settings import settings_router

app = FastAPI(title="TG Football Mini App API", docs_url=None, redoc_url=None)

import os
_origins = ["http://localhost:5173"]
if os.getenv("WEBAPP_ORIGIN"):  # e.g. https://app.football-blitz.online at deploy
    _origins.append(os.getenv("WEBAPP_ORIGIN"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(player_router, prefix="/api")
app.include_router(leagues_router, prefix="/api")
app.include_router(matches_router, prefix="/api")
app.include_router(hall_of_fame_router, prefix="/api")
app.include_router(training_router, prefix="/api")
app.include_router(shop_router, prefix="/api")
app.include_router(settings_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"ok": True}
