from aiohttp.web import Request, Response, json_response, HTTPBadRequest
from pydantic import BaseModel, ValidationError, constr
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from logging_config import logger

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
            logger.error(E)
            return self.BAD(error = E)
        
        except Exception as E:
            return self.BAD(error = str(E), status=500)
    
    @classmethod
    async def router(cls, request: Request) -> Response:
        obj = cls(request)
        
        if not obj.method_is_valid:
            return obj.BAD(error = "Not valid method")
        
        obj.data = await obj.get_data()
        return await obj.handle_request()