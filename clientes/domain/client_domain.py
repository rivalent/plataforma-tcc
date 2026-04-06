from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

@dataclass
class ClientDomain:
    name: str
    surname: str
    email: str
    birthdate: date
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    inactive_at: Optional[datetime] = None
    active: bool = True
