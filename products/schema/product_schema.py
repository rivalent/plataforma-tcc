from pydantic import BaseModel, Field
from typing import Optional

class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    desc: str = Field(..., max_length=1000)
    price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=0)

class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    desc: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., ge=0)
    quantity: Optional[int] = Field(None, ge=0)
