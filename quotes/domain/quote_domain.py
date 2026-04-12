from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class QuoteDomain:
    code: str
    value: float
    created_at: Optional[datetime] = None
