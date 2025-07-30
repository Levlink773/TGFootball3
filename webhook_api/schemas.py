from pydantic import BaseModel, HttpUrl, condecimal, Field
from typing import List, Optional



class MonoResultSchema(BaseModel):
    invoiceId: str            
    status: str          
    amount: int         
    ccy: int               
    createdDate: str     
    modifiedDate: str        
    reference: str     
    destination: str
