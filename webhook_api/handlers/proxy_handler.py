from aiohttp import ClientSession
from aiohttp.web import Response

from config import TARGET_BLITZ_HOST
from ..base_endpoint import EndPoint, HTTPMethod

class ProxyEndpoint(EndPoint):
    method = HTTPMethod.POST  # чтобы принимать все методы (GET, POST, PUT и т.д.)

    async def handle_request(self) -> Response:
        """
        Проксирует запрос на другой сервер, сохраняя:
        - путь (URL)
        - метод
        - тело запроса
        - заголовки
        """
        target_url = f"{TARGET_BLITZ_HOST}{self.request.rel_url}"

        # Копируем заголовки кроме Host
        headers = {k: v for k, v in self.request.headers.items() if k.lower() != 'host'}
        body = await self.request.read()

        async with ClientSession() as session:
            async with session.request(
                method=self.request.method,
                url=target_url,
                headers=headers,
                data=body,
                allow_redirects=False
            ) as resp:
                # Пересылаем ответ обратно клиенту
                response_body = await resp.read()
                return Response(
                    body=response_body,
                    status=resp.status,
                    headers=resp.headers
                )
