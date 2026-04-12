from quotes.domain.quote_domain import QuoteDomain
from typing import Protocol, Optional

class QuoteRepository(Protocol):
    def get_by_code(self, code: str) -> Optional[QuoteDomain]:
        pass
        
    def save(self, quote: QuoteDomain) -> QuoteDomain:
        pass