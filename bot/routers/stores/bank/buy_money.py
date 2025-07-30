from aiogram import Router, F
from aiogram.types import CallbackQuery

from api.monobank.create_payment import CreatePayment


from bot.callbacks.bank_callbacks import (
    SelectTypeMoneyPack
)
from bot.keyboards.bank_keyboard import (
    select_type_money_pack,
    buy_current_pack
)
from database.models.character import Character

from services.payment_service import PaymentServise

from constants import BANK_PHOTO
from config import CALLBACK_URL_WEBHOOK_MONEY

from .types import MoneyPack, money_packs

bank_router = Router()

@bank_router.callback_query(
    F.data == "bank"
)
async def views_type_money_pack(
    querry: CallbackQuery
):
    text = """
<b>Поповнюй свій баланс монет та ставай королем гри!</b> 💰👑

Потрібні монети, щоб покращити свого героя чи відкрити нові можливості? Вибирай свій ідеальний пак монет прямо зараз!  

🔥 <b>Наші пропозиції:</b>  
- <b>Small Money Pack</b> — <b>100 монет</b> за <b>150 грн</b>. Ідеально для швидкого старту!  
- <b>Middle Money Pack</b> — <b>250 монет</b> за <b>330 грн</b>. Більше монет — більше можливостей!  
- <b>Big Money Pack</b> — <b>500 монет</b> за <b>590 грн</b>. Відчуй справжній прогрес!  
- <b>King Money Pack</b> — <b>1000 монет</b> за <b>990 грн</b>. Твій шлях до абсолютної переваги! 👑  

💎 Чому це вигідно?  
- Отримай монети за вигідними цінами!  
- Відкривай нові горизонти в грі!  
- Здобувай перевагу перед іншими гравцями!  

Не відкладай успіх на завтра — поповнюй баланс уже сьогодні та стань лідером гри! ⚽  
"""
    await querry.message.answer_photo(
        photo=BANK_PHOTO,
        caption=text,
        reply_markup=select_type_money_pack()
    )
    
@bank_router.callback_query(
    SelectTypeMoneyPack.filter()
)
async def select_money_pack(
    query: CallbackQuery,
    callback_data: SelectTypeMoneyPack,
    character: Character
):    
    money_pack: MoneyPack = money_packs.get(callback_data.type_money_pack) 
    
    text = f"""
<b>Ти обрав {money_pack.name}!</b> 💰

- <b>Кількість монет:</b> {money_pack.coins} монет  
- <b>Ціна:</b> {money_pack.price} грн  

Це чудовий вибір для того, щоб прискорити свій прогрес у грі! Завдяки цьому паку ти зможеш:  
- Покращити свого героя  
- Отримати нові можливості  
- Підвищити свої шанси на перемогу ⚽  

<b>Натискай "Придбати" та поповнюй баланс прямо зараз!</b>
"""

    payment = CreatePayment(
        price        = money_pack.price,
        name_product = money_pack.name,
        webhook_url  = CALLBACK_URL_WEBHOOK_MONEY
    )
    url_payment_response = await payment.send_request()
    if not url_payment_response:
        return await query.answer("Сталася помилка під час створення платежу")
    
    order_id = url_payment_response['invoiceId']
    url_payment = url_payment_response['pageUrl']
    
    payment = await PaymentServise.create_payment(
        price    = money_pack.price,
        user_id  = character.characters_user_id,
        order_id = order_id,
    )
    
    await PaymentServise.create_money_payment(
        order_id    = payment.order_id,
        count_money = money_pack.coins
    )    

    await query.message.answer_photo(
        photo=BANK_PHOTO,
        caption=text,
        reply_markup=buy_current_pack(
            url_payment=url_payment
        )
    )