from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ProductDomain:
    name: str
    desc: str
    price: float
    quantity: int
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    inactive_at: Optional[datetime] = None
    active: bool = True
