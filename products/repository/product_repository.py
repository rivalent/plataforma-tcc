from products.domain.product_domain import ProductDomain
from typing import Protocol, Optional

class ProductRepository(Protocol):
    def create(self, product: ProductDomain) -> ProductDomain:
        pass

    def get_by_id(self, id: str) -> Optional[ProductDomain]:
        pass

    def search(
        self, 
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None, 
        name_or_desc: Optional[str] = None, 
        min_quantity: Optional[int] = None
    ) -> list[ProductDomain]:
        pass

    def update(self, product: ProductDomain) -> Optional[ProductDomain]:
        pass

    def delete(self, id: str) -> bool:
        pass
