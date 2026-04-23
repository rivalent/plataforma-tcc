from pydantic import BaseModel, Field
from typing import List

class SaleItemCreateRequest(BaseModel):
    product_id: str = Field(...)
    quantity: int = Field(..., gt=0)

class SaleCreateRequest(BaseModel):
    client_id: str = Field(...)
    items: List[SaleItemCreateRequest] = Field(..., min_length=1)