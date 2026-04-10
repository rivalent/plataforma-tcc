from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Optional

class ClientCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    surname: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    birthdate: date

class ClientUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    surname: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    birthdate: Optional[date] = None
