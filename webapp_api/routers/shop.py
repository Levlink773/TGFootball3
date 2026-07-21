import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from aiogram.utils.web_app import WebAppInitData

from constants import CONST_PRICE_ENERGY, lootboxes, PRICE_CHANGE_POSITION, PRICE_TRAINING_KEY

from bot.routers.stores.vip_pass.types import vip_passes
from bot.routers.stores.bank.types import money_packs

from services.character_service import CharacterService
from services.items_service import ItemService

from webapp_api.auth import auth_user

shop_router = APIRouter()

_ROOT = Path(__file__).resolve().parent.parent.parent
CATALOG_ITEMS = json.loads((_ROOT / "items.json").read_text(encoding="utf-8"))
CATALOG_LUXE_ITEMS = json.loads((_ROOT / "luxe_items.json").read_text(encoding="utf-8"))

STATIC_CATALOG = {
    "items": CATALOG_ITEMS,
    "luxe_items": CATALOG_LUXE_ITEMS,
    "boxes": [
        {"key": key, **{k: v for k, v in box.items()}}
        for key, box in lootboxes.items()
        if box["price"] is not None
    ],
    "energy": [{"amount": amount, "price_uah": price} for amount, price in CONST_PRICE_ENERGY.items()],
    "coins": [
        {"key": pack_type.value, "name": pack.name, "coins": pack.coins, "price_uah": pack.price}
        for pack_type, pack in money_packs.items()
    ],
    "vip": [
        {"key": pass_type.value, "duration_days": pack.duration, "price_uah": pack.price}
        for pass_type, pack in vip_passes.items()
    ],
    "change_position_price": PRICE_CHANGE_POSITION,
    "training_key_price_uah": PRICE_TRAINING_KEY,
}


@shop_router.get("/shop")
async def get_shop(auth: WebAppInitData = Depends(auth_user)):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")

    owned = await ItemService.get_items_from_character(character.id) or []
    return {
        **STATIC_CATALOG,
        "me": {
            "money": character.money,
            "energy": character.current_energy,
            "level": character.level,
            "vip_active": character.vip_pass_is_active,
            "owned_items": [
                {"id": item.id, "name": item.name, "category": item.category}
                for item in owned
            ],
            "equipped": {
                "t_shirt_id": character.t_shirt_id,
                "shorts_id": character.shorts_id,
                "gaiters_id": character.gaiters_id,
                "boots_id": character.boots_id,
            },
        },
    }
