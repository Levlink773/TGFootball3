from aiohttp.web import Request, Response, json_response, HTTPBadRequest
from pydantic import BaseModel, ValidationError, constr
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from logging_config import logger
from webhook_api.monobank_signature import MonobankSignatureVerifier

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    
class ResponseAnswer:
    def OK(self, **kwargs):
        return json_response({"status": "OK", **kwargs}, status=200)
    
    def BAD(self,status:Optional[int] = 400, **kwargs):
        return json_response({"status": "BAD", **kwargs}, status=status)
    

class EndPoint(ABC, ResponseAnswer):
    request: Request

    schema: BaseModel
    method: HTTPMethod

    # When True, the X-Sign header is verified against Monobank's public key
    # before the body is parsed or the handler runs.
    verify_signature: bool = False

    data: dict = None
    
    def __init__(self, request: Request) -> None:
        self.request = request
        self.data = None
        
    @abstractmethod
    async def handle_request(self) -> Response:
        pass
    
    
    @property
    def method_is_valid(self) -> bool:
        return self.request.method == self.method.value
    
    async def get_data(self) -> BaseModel:  
        try:
            data = await self.request.json()
            data = self.schema(**data)
            return data
        except ValidationError as E:
            # Never echo the exception to the caller: this is an internet-facing
            # payment endpoint. (A ValidationError object is also not JSON
            # serialisable, so returning it made the error handler itself throw.)
            logger.error("webhook payload failed validation: %s", E)
            return self.BAD(error = "Invalid payload")

        except Exception as E:
            logger.error("webhook body parse failed: %s", E)
            return self.BAD(error = "Bad request")
    
    @classmethod
    async def router(cls, request: Request) -> Response:
        obj = cls(request)

        if not obj.method_is_valid:
            return obj.BAD(error = "Not valid method")

        if cls.verify_signature:
            body = await request.read()
            x_sign = request.headers.get("X-Sign")
            if not await MonobankSignatureVerifier.verify(x_sign, body):
                logger.error("Rejected webhook with invalid Monobank signature")
                return obj.BAD(error="Invalid signature", status=403)

        obj.data = await obj.get_data()
        if isinstance(obj.data, Response):
            # Body failed to parse — get_data already built the error response.
            # Reaching handle_request here would AttributeError on self.data.invoiceId.
            return obj.data
        return await obj.handle_request()