from sales.domain.sales_domain import SaleDomain
from typing import Protocol, List, Optional

class SaleRepository(Protocol):
    def save(self, sale: SaleDomain) -> SaleDomain:
        pass

    def get_by_id(self, sale_id: str) -> Optional[SaleDomain]:
        pass

    def get_by_product(self, product_id: str) -> List[SaleDomain]:
        pass

    def get_by_status(self, status: int) -> List[SaleDomain]:
        pass

    def count_by_product_and_status(self, product_id: str, status: int) -> int:
        pass
