from aiohttp import ClientTimeout, ClientSession, ClientResponse

from logging_config import logger
from enum import StrEnum

from abc import ABC, abstractclassmethod
from typing import Union

class HttpMethods(StrEnum):
    GET  = "get"
    POST = "post"


class Client(ABC):
    url = None
    method: HttpMethods
    timeot = ClientTimeout(total=10)

    def __get_session(self) -> ClientSession:
        return ClientSession(timeout=self.timeot)
    
    
    async def _request(self, url: str, **kwargs) -> Union[str,dict,None]:
        session = self.__get_session()
        try:
            async with session.request(method=self.method, url=url, **kwargs) as response:
                
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    response_answer =  await response.json()
                else:
                    response_answer =  await response.text()
                    
                response.raise_for_status()
                return response_answer
        except Exception as E:
            logger.error(f"error send request err: {E}")
            logger.error(f"err response - {response_answer}")
        finally:
            await session.close()

        
    @abstractclassmethod
    async def send_request(self) -> ClientResponse:
        ...
        
        