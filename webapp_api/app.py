"""TG Football Mini App API — sidecar FastAPI service (port 3004).

Reads the same MySQL as the bot via the bot's own services/models.
Run: uvicorn webapp_api.app:app --host 127.0.0.1 --port 3004
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.base_acces import get_base
get_base()  # register ALL models so string-name relationships resolve

from webapp_api.routers.player import player_router

app = FastAPI(title="TG Football Mini App API", docs_url=None, redoc_url=None)

# ponytail: origins list gets the real app domain at deploy; localhost for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(player_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"ok": True}
