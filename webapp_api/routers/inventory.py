import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from aiogram.utils.web_app import WebAppInitData

from constants import PROCENT_TO_SELL
from services.character_service import CharacterService
from services.items_service import ItemService
from webapp_api.auth import auth_user

inventory_router = APIRouter()

CATEGORIES = ("T_SHIRT", "SHORTS", "GAITERS", "BOOTS")
_CATEGORY_FIELD = {
    "T_SHIRT": "t_shirt_id",
    "SHORTS": "shorts_id",
    "GAITERS": "gaiters_id",
    "BOOTS": "boots_id",
}


def _item_payload(item) -> dict:
    category = item.category.value if hasattr(item.category, "value") else item.category
    return {
        "id": item.id,
        "name": item.name,
        "category": category,
        "price": item.price,
        "sell_price": round(item.price * (PROCENT_TO_SELL / 100)),
        "level_required": item.level_required,
        "stats": json.loads(item.stats) if item.stats else {},
    }


async def _get_character(auth: WebAppInitData):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")
    return character


@inventory_router.get("/inventory")
async def get_inventory(auth: WebAppInitData = Depends(auth_user)):
    character = await _get_character(auth)
    owned = await ItemService.get_items_from_character(character.id) or []
    return {
        "items": [_item_payload(i) for i in owned],
        "equipped": {field: getattr(character, field) for field in _CATEGORY_FIELD.values()},
        "sell_percent": PROCENT_TO_SELL,
        "money": character.money,
    }


class ItemRequest(BaseModel):
    item_id: int


class UnequipRequest(BaseModel):
    category: str


async def _owned_item_or_404(character, item_id: int):
    item = await ItemService.get_item(item_id=item_id)
    if not item or item.owner_character_id != character.id:
        raise HTTPException(status_code=404, detail="Річ не знайдено")
    return item


@inventory_router.post("/inventory/equip")
async def equip_item(req: ItemRequest, auth: WebAppInitData = Depends(auth_user)):
    character = await _get_character(auth)
    item = await _owned_item_or_404(character, req.item_id)
    if character.level < (item.level_required or 0):
        raise HTTPException(status_code=400, detail="Не вистачає рівня, щоб одягнути цю річ")
    await CharacterService.equip_item(character_obj=character, item_obj=item)
    return {"ok": True, "item": _item_payload(item)}


@inventory_router.post("/inventory/unequip")
async def unequip_item(req: UnequipRequest, auth: WebAppInitData = Depends(auth_user)):
    if req.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Невірна категорія")
    character = await _get_character(auth)
    await ItemService.unequip_item(character, req.category)
    return {"ok": True}


@inventory_router.post("/inventory/sell")
async def sell_item(req: ItemRequest, auth: WebAppInitData = Depends(auth_user)):
    # Mirrors the bot's SellMyItem flow: unequip if worn, credit PROCENT_TO_SELL% of
    # price, delete the item. Same price rules as bot/routers/character/items_character.py.
    character = await _get_character(auth)
    item = await _owned_item_or_404(character, req.item_id)

    equipped_ids = [getattr(character, f) for f in _CATEGORY_FIELD.values()]
    category = item.category.value if hasattr(item.category, "value") else item.category
    if item.id in equipped_ids:
        await ItemService.unequip_item(character, category)

    sell_price = round(item.price * (PROCENT_TO_SELL / 100))
    # Delete first, atomically scoped to the owner: only the request that actually
    # removes the row gets the payout (concurrent double-sell = money printing).
    deleted = await ItemService.delete_item_owned(
        item_id=req.item_id, owner_character_id=character.id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Річ не знайдено")
    await CharacterService.update_money_character(
        character_id=character.id, amount_money_adjustment=sell_price
    )
    return {"ok": True, "sold_for": sell_price, "money": character.money + sell_price}
