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
    prices: Optional[dict] = None

    def calculate_prices_from_quotes(self, quotes: dict):
        self.prices = {'BRL': self.price}
        for currency, rate in quotes.items():
            self.prices[currency] = round(self.price / rate, 2)
