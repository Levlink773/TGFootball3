from aiohttp import web
import asyncio

from loader import bot, dp, app
from bot.routers.router import main_router
from bot.middlewares import handlers
from load_utils import start_utils
from logging_config import logger
from utils.schema_guard import check_schema_at_head

from webhook_api.handlers.energy_handler import MonoResultEnergy
from webhook_api.handlers.box_handler import MonoResultBox
from webhook_api.handlers.change_position_handler import MonoResultChangePosition
from webhook_api.handlers.money_handler import MonoResultMoney
from webhook_api.handlers.proxy_handler import ProxyEndpoint
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
    CALLBACK_URL_WEBHOOK_BUY_TRAINING_KEY, CALLBACK_URL_WEBHOOK_ENERGY_BLITZ, CALLBACK_URL_WEBHOOK_BOX_BLITZ,
    CALLBACK_URL_WEBHOOK_VIP_PASS_BLITZ, CALLBACK_URL_WEBHOOK_MONEY_BLITZ
)

dp.include_router(main_router)
    

async def start_polling():
    for _attempt in range(3):
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            break
        except Exception as _e:
            logger.warning("delete_webhook failed at startup (attempt %s): %s", _attempt + 1, _e)
            await asyncio.sleep(2)
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
    # Football Blitz proxy
    app.router.add_post("/" + CALLBACK_URL_WEBHOOK_ENERGY_BLITZ.split("/")[-1], ProxyEndpoint.router)
    app.router.add_post("/" + CALLBACK_URL_WEBHOOK_BOX_BLITZ.split("/")[-1], ProxyEndpoint.router)
    app.router.add_post("/" + CALLBACK_URL_WEBHOOK_VIP_PASS_BLITZ.split("/")[-1], ProxyEndpoint.router)
    app.router.add_post("/" + CALLBACK_URL_WEBHOOK_MONEY_BLITZ.split("/")[-1], ProxyEndpoint.router)

    
async def main():
    await check_schema_at_head()  # canary: log-only, warns if DB schema drifts from code
    await start_utils()
    await asyncio.gather(
        start_weebhook(),
        start_polling()
    )
if __name__ == "__main__":
    import sys
    from utils.coordination import single_instance_lock
    if not single_instance_lock():
        sys.exit(1)
    asyncio.run(main())


"""
alembic revision --autogenerate -m "add new realship to Item"
alembic upgrade head
"""