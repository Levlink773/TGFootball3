from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery

from api.monobank.create_payment import CreatePayment

from bot.training.keyboard.buy_training_key import buy_training_key

from database.models.character import Character

from constants import PRICE_TRAINING_KEY, BUY_TRAINING_KEY
from config import CALLBACK_URL_WEBHOOK_BUY_TRAINING_KEY

from services.payment_service import PaymentServise

buy_training_key_router = Router()

TRAINING_KEY_PURCHASE = """
🔑 <b>Придбання ключа для тренування</b> ⚽🔥  

Щоб взяти участь у тренувальній сесії, тобі потрібен спеціальний ключ. 🏆  
Він дає доступ до тренувань, де ти зможеш прокачати свої навички та стати ще кращим гравцем! 💪⚡  

💰 <b>Вартість ключа:</b> {price} UAH
🛒 <i>Натисни кнопку нижче, щоб придбати ключ і підготуватися до тренування!</i> 🚀
"""

@buy_training_key_router.callback_query(F.data == "buy_training_key")
async def buy_training_key_hander(
    query: CallbackQuery,
    character: Character
):
    await query.message.edit_reply_markup(
        reply_markup = None
    )
    payment = CreatePayment(
        price=PRICE_TRAINING_KEY,
        name_product="buy training key",
        webhook_url=CALLBACK_URL_WEBHOOK_BUY_TRAINING_KEY
    )
    url_payment_response = await payment.send_request()
    if not url_payment_response:
        return await query.answer("Сталася помилка під час створення платежу")
    
    order_id = url_payment_response['invoiceId']
    url_payment = url_payment_response['pageUrl']
    
    payment = await PaymentServise.create_payment(
        price    = PRICE_TRAINING_KEY,
        user_id  = character.characters_user_id,
        order_id = order_id,
    )
    
    await PaymentServise.create_buy_training_key_payment(
        order_id = payment.order_id,
    )
    
    await query.message.answer_photo(
        photo=BUY_TRAINING_KEY,
        caption=TRAINING_KEY_PURCHASE.format(
            price = PRICE_TRAINING_KEY
        ),
        reply_markup = buy_training_key(url_payment)
    )