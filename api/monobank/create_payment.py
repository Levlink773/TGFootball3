import uuid
import random

from config import TOKEN_MONOBANK
from api.client import Client, HttpMethods

from loader import bot

class CreatePayment(Client):
    url = "https://api.monobank.ua/api/merchant/invoice/create"
    
    headers = {
        "X-token" : TOKEN_MONOBANK,
        "Content-Type" : "application/json"

    }
    
    method = HttpMethods.POST.value
    data = None
    
    def __init__(
        self, 
        price: int, 
        name_product: str,
        webhook_url: str
    ) -> None:
        self.price = price
        self.name_product = name_product
        self.webhook_url = webhook_url
        
    def _generate_hash(self) -> str:
        return str(uuid.uuid4())[:10]
    
    def _get_random_num(self) -> int:
        return random.randint(1,10)
    
    async def _get_return_url(self):
        bot_me = await bot.get_me()
        return f"https://t.me/{bot_me.username}"
        
    async def send_request(self):

        data = {
            "amount"    :  self.price*100,
            "ccy"       : 980,
            "merchantPaymInfo" : {
                "reference": self._generate_hash(),
                "destination": f"Покупка {self.name_product}",
                "comment": f"Покупка {self.name_product}",
            
            },
            "webHookUrl" : self.webhook_url,
            "redirectUrl"   : await self._get_return_url()
        }
        
        return await self._request(
            url=self.url,
            json= data,
            headers = self.headers
        )