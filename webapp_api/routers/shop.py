import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from aiogram.utils.web_app import WebAppInitData

from constants import CONST_PRICE_ENERGY, lootboxes, PRICE_CHANGE_POSITION, PRICE_TRAINING_KEY
from config import (
    PositionCharacter,
    CALLBACK_URL_WEBHOOK_ENERGY,
    CALLBACK_URL_WEBHOOK_BOX,
    CALLBACK_URL_WEBHOOK_VIP_PASS,
    CALLBACK_URL_WEBHOOK_MONEY,
    CALLBACK_URL_WEBHOOK_CHANGE_POSITION,
    CALLBACK_URL_WEBHOOK_BUY_TRAINING_KEY,
)

from api.monobank.create_payment import CreatePayment
from bot.routers.stores.vip_pass.types import vip_passes, VipPassTypes
from bot.routers.stores.bank.types import money_packs, MoneyPackType
from database.models.types import TypeBox
from database.models.item import Item

from services.character_service import CharacterService
from services.items_service import ItemService
from services.payment_service import PaymentServise

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


# --- Monobank invoices (reuses bot flow: CreatePayment + per-product payment rows;
#     webhooks on the bot's aiohttp app finish the purchase, UNCHANGED) ---

class InvoiceRequest(BaseModel):
    product_type: str   # energy | box | coins | vip | change_position | training_key
    product_key: str | int | None = None


async def _build_invoice(req: InvoiceRequest) -> tuple[int, str, str, str]:
    """Returns (price_uah, product_name, webhook_url, kind_key). Raises HTTPException 400."""
    t = req.product_type
    if t == "energy":
        try:
            amount = int(req.product_key)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Невірна кількість енергії")
        if amount not in CONST_PRICE_ENERGY:
            raise HTTPException(status_code=400, detail="Невірна кількість енергії")
        return CONST_PRICE_ENERGY[amount], f"Buy {amount} energy", CALLBACK_URL_WEBHOOK_ENERGY, str(amount)
    if t == "box":
        box = lootboxes.get(req.product_key)
        if not box or box["price"] is None:
            raise HTTPException(status_code=400, detail="Невірний бокс")
        return box["price"], box["name_lootbox"], CALLBACK_URL_WEBHOOK_BOX, req.product_key
    if t == "coins":
        try:
            pack_type = MoneyPackType(req.product_key)
        except ValueError:
            raise HTTPException(status_code=400, detail="Невірний пак монет")
        pack = money_packs[pack_type]
        return pack.price, pack.name, CALLBACK_URL_WEBHOOK_MONEY, pack_type.value
    if t == "vip":
        try:
            pass_type = VipPassTypes(req.product_key)
        except ValueError:
            raise HTTPException(status_code=400, detail="Невірний VIP-пак")
        pack = vip_passes[pass_type]
        return pack.price, f"VIP pass {pack.duration} days", CALLBACK_URL_WEBHOOK_VIP_PASS, pass_type.value
    if t == "change_position":
        try:
            position = PositionCharacter(req.product_key)
        except ValueError:
            raise HTTPException(status_code=400, detail="Невірна позиція")
        return PRICE_CHANGE_POSITION, f"Зміна позиції на {position.value}", CALLBACK_URL_WEBHOOK_CHANGE_POSITION, position.value
    if t == "training_key":
        return PRICE_TRAINING_KEY, "Ключ тренування", CALLBACK_URL_WEBHOOK_BUY_TRAINING_KEY, ""
    raise HTTPException(status_code=400, detail="Невірний тип товару")


@shop_router.post("/shop/invoice")
async def create_invoice(req: InvoiceRequest, auth: WebAppInitData = Depends(auth_user)):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")

    price, name, webhook_url, kind_key = await _build_invoice(req)
    if not webhook_url:
        raise HTTPException(status_code=503, detail="Оплата тимчасово недоступна")

    response = await CreatePayment(price=price, name_product=name, webhook_url=webhook_url).send_request()
    if not response:
        raise HTTPException(status_code=502, detail="Не вдалося створити платіж")

    order_id = response["invoiceId"]
    await PaymentServise.create_payment(price=price, user_id=character.characters_user_id, order_id=order_id)

    t = req.product_type
    if t == "energy":
        await PaymentServise.create_energy_payment(order_id=order_id, amount_energy=int(kind_key))
    elif t == "box":
        await PaymentServise.create_box_payment(order_id=order_id, type_box=TypeBox(kind_key))
    elif t == "coins":
        pack = money_packs[MoneyPackType(kind_key)]
        await PaymentServise.create_money_payment(order_id=order_id, count_money=pack.coins)
    elif t == "vip":
        await PaymentServise.create_vip_pass_payment(order_id=order_id, type_vip_pass=VipPassTypes(kind_key))
    elif t == "change_position":
        await PaymentServise.create_change_position_payment(order_id=order_id, position=PositionCharacter(kind_key))
    elif t == "training_key":
        await PaymentServise.create_buy_training_key_payment(order_id=order_id)

    return {"invoice_id": order_id, "url": response["pageUrl"], "price_uah": price}


# --- In-game item purchase (coins), mirrors bot items_store flow ---

class BuyItemRequest(BaseModel):
    item_id: int
    luxe: bool = False


@shop_router.post("/shop/buy-item")
async def buy_item(req: BuyItemRequest, auth: WebAppInitData = Depends(auth_user)):
    character = await CharacterService.get_character(character_user_id=auth.user.id)
    if not character:
        raise HTTPException(status_code=404, detail="No character")

    catalog = CATALOG_LUXE_ITEMS if req.luxe else CATALOG_ITEMS
    item = next((i for i in catalog if i["id"] == req.item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Річ не знайдено")
    if character.money < item["price"]:
        raise HTTPException(status_code=400, detail="Не вистачає монет на купівлю цієї речі")
    if character.level < item["level_required"]:
        raise HTTPException(status_code=400, detail="Не вистачає рівня, щоб купити цю річ")

    item_obj = Item(
        name=item["name"],
        category=item["category"],
        level_required=item["level_required"],
        price=item["price"],
        stats=json.dumps(item["stats"]),
        owner_character_id=character.id,
    )
    await ItemService.create_item(item_obj=item_obj)
    await CharacterService.update_money_character(
        character_id=character.id,
        amount_money_adjustment=-item_obj.price,
    )

    return {"ok": True, "item": {"id": item["id"], "name": item["name"]}, "money": character.money - item["price"]}
