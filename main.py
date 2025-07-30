from aiohttp import web
import asyncio

from loader import bot, dp, app
from bot.routers.router import main_router
from bot.middlewares import handlers
from load_utils import start_utils

from webhook_api.handlers.energy_handler import MonoResultEnergy
from webhook_api.handlers.box_handler import MonoResultBox
from webhook_api.handlers.change_position_handler import MonoResultChangePosition
from webhook_api.handlers.money_handler import MonoResultMoney
from webhook_api.handlers.vip_pass_handler import MonoResultVipPass
from webhook_api.handlers.key_handler import MonoResultBuyTrainingKey

from config import (
    WEBAPP_HOST, 
    WEBAPP_PORT, 
    CALLBACK_URL_WEBHOOK_ENERGY, 
    CALLBACK_URL_WEBHOOK_BOX,
    CALLBACK_URL_WEBHOOK_CHANGE_POSITION,
    CALLBACK_URL_WEBHOOK_MONEY,
    CALLBACK_URL_WEBHOOK_VIP_PASS,
    CALLBACK_URL_WEBHOOK_BUY_TRAINING_KEY
)

dp.include_router(main_router)
    

async def start_polling():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
async def start_weebhook():
    add_patch_payments()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)    
    await site.start()
    

def add_patch_payments():
    app.router.add_post("/" + CALLBACK_URL_WEBHOOK_ENERGY.split("/")[-1], MonoResultEnergy.router)
    app.router.add_post("/" + CALLBACK_URL_WEBHOOK_BOX.split("/")[-1], MonoResultBox.router)
    app.router.add_post("/" + CALLBACK_URL_WEBHOOK_CHANGE_POSITION.split("/")[-1], MonoResultChangePosition.router)
    app.router.add_post("/" + CALLBACK_URL_WEBHOOK_MONEY.split("/")[-1], MonoResultMoney.router)
    app.router.add_post("/" + CALLBACK_URL_WEBHOOK_VIP_PASS.split("/")[-1], MonoResultVipPass.router)
    app.router.add_post("/" + CALLBACK_URL_WEBHOOK_BUY_TRAINING_KEY.split("/")[-1], MonoResultBuyTrainingKey.router)

    
async def main():
    await start_utils()
    from match.test import test
    asyncio.create_task(test())
    await asyncio.gather(
        start_weebhook(),
        start_polling()
    )
if __name__ == "__main__":
    asyncio.run(main())


"""
alembic revision --autogenerate -m "add new realship to Item"
alembic upgrade head
"""