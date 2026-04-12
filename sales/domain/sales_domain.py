from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum

class SaleStatus(Enum):
    STARTED = 0
    PROGRESS = 1
    DONE = 2
    CANCELED = 3

@dataclass
class SaleItemDomain:
    sell_id: str
    product_id: str
    quantity: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class SaleDomain:
    id: str
    client_id: str
    status: int
    items: List[SaleItemDomain]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
