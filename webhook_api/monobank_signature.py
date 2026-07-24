import base64

import aiohttp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature

from config import TOKEN_MONOBANK
from logging_config import logger

PUBKEY_URL = "https://api.monobank.ua/api/merchant/pubkey"


class MonobankSignatureVerifier:
    """Verifies the X-Sign header Monobank attaches to every webhook.

    Monobank signs the raw request body with its private key (ECDSA / SHA256).
    The matching public key is fetched once from the merchant API and cached.
    """

    _pub_key_pem: bytes | None = None

    @classmethod
    async def _get_pub_key_pem(cls) -> bytes | None:
        if cls._pub_key_pem is not None:
            return cls._pub_key_pem
        if not TOKEN_MONOBANK:
            return None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    PUBKEY_URL, headers={"X-Token": TOKEN_MONOBANK}
                ) as resp:
                    data = await resp.json()
            cls._pub_key_pem = base64.b64decode(data["key"])
            return cls._pub_key_pem
        except Exception as e:
            logger.error(f"Monobank pubkey fetch failed: {e}")
            return None

    @classmethod
    async def verify(cls, x_sign: str | None, body: bytes) -> bool:
        # Fail CLOSED: without the merchant token we cannot fetch Monobank's public
        # key, so the callback is unverifiable — and an unverified callback credits
        # real coins. Refuse it rather than trust it.
        if not TOKEN_MONOBANK:
            logger.error(
                "TOKEN_MONOBANK not set; REJECTING webhook (cannot verify signature)"
            )
            return False
        if not x_sign:
            return False
        pub_pem = await cls._get_pub_key_pem()
        if not pub_pem:
            return False
        try:
            pub_key = serialization.load_pem_public_key(pub_pem)
            signature = base64.b64decode(x_sign)
            pub_key.verify(signature, body, ec.ECDSA(hashes.SHA256()))
            return True
        except (InvalidSignature, Exception) as e:
            logger.error(f"Monobank signature verification failed: {e}")
            return False
