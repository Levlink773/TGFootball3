from aiohttp import ClientSession
from aiohttp.web import Response

from config import (
    TARGET_BLITZ_HOST,
    CALLBACK_URL_WEBHOOK_ENERGY_BLITZ,
    CALLBACK_URL_WEBHOOK_BOX_BLITZ,
    CALLBACK_URL_WEBHOOK_VIP_PASS_BLITZ,
    CALLBACK_URL_WEBHOOK_MONEY_BLITZ,
)
from logging_config import logger
from webhook_api.monobank_signature import MonobankSignatureVerifier
from ..base_endpoint import EndPoint, HTTPMethod


def _allowed_path(url: str | None) -> str | None:
    if not url:
        return None
    return "/" + url.split("/")[-1]


# Only these exact paths may be proxied to the blitz host. Anything else is rejected.
ALLOWED_PROXY_PATHS = {
    p
    for p in (
        _allowed_path(CALLBACK_URL_WEBHOOK_ENERGY_BLITZ),
        _allowed_path(CALLBACK_URL_WEBHOOK_BOX_BLITZ),
        _allowed_path(CALLBACK_URL_WEBHOOK_VIP_PASS_BLITZ),
        _allowed_path(CALLBACK_URL_WEBHOOK_MONEY_BLITZ),
    )
    if p
}


class ProxyEndpoint(EndPoint):
    method = HTTPMethod.POST

    # One session per process instead of one per request.
    _session: ClientSession | None = None

    @classmethod
    def _get_session(cls) -> ClientSession:
        if cls._session is None or cls._session.closed:
            cls._session = ClientSession()
        return cls._session

    async def handle_request(self) -> Response:
        """Proxy a verified Monobank webhook to the blitz host.

        Verifies the X-Sign signature, then forwards only whitelisted paths.
        """
        body = await self.request.read()

        x_sign = self.request.headers.get("X-Sign")
        if not await MonobankSignatureVerifier.verify(x_sign, body):
            logger.error("Rejected proxy webhook with invalid Monobank signature")
            return self.BAD(error="Invalid signature", status=403)

        request_path = self.request.rel_url.path
        if request_path not in ALLOWED_PROXY_PATHS:
            logger.error(f"Rejected proxy to disallowed path: {request_path}")
            return self.BAD(error="Path not allowed", status=403)

        target_url = f"{TARGET_BLITZ_HOST}{self.request.rel_url}"
        headers = {k: v for k, v in self.request.headers.items() if k.lower() != "host"}

        session = self._get_session()
        async with session.request(
            method=self.request.method,
            url=target_url,
            headers=headers,
            data=body,
            allow_redirects=False,
        ) as resp:
            response_body = await resp.read()
            return Response(
                body=response_body,
                status=resp.status,
                headers=resp.headers,
            )
