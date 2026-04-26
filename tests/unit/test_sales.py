from sales.service.sales_service import SalesService
from sales.repository.sqlite_sales_repository import SqliteSalesRepository
from sales.domain.sales_domain import SaleStatus
from shared.database import SqliteManager
import os
import pytest

class FakeGateway:
    def get_client(self, client_id):
        if client_id == "CLI-GOKU":
            return {"id": "CLI-GOKU", "name": "Son Goku"}
        return None

    def get_product(self, product_id):
        if product_id == "PROD-SENZU":
            return {"id": "PROD-SENZU", "name": "Senzu Bean", "price": 500.00, "quantity": 10}
        return None

    def update_product_stock(self, product_id, new_qty):
        pass

    def get_all_quotes(self):
        return [
            {"code": "USD", "value": 5.0},
            {"code": "EUR", "value": 6.0}
        ]

test_manager = SqliteManager("sales/database", "db_test_sales.db")
test_repo = SqliteSalesRepository(test_manager)
test_repo.create_tables()
test_service = SalesService(test_repo, FakeGateway())

created_sale_id = None

def test_save_sale_successfully():
    global created_sale_id

    items_to_buy = [{"product_id": "PROD-SENZU", "quantity": 2}]
    
    new_sale = test_service.save_sale(client_id="CLI-GOKU", items_data=items_to_buy)
    
    assert new_sale.id is not None
    assert new_sale.client_id == "CLI-GOKU"
    assert new_sale.status == SaleStatus.STARTED.value
    assert len(new_sale.items) == 1
    
    created_sale_id = new_sale.id

def test_prevent_sale_with_nonexistent_product():
    items_to_buy = [{"product_id": "GHOST-PROD", "quantity": 1}]

    with pytest.raises(Exception) as exc_info:
        test_service.save_sale(client_id="CLI-GOKU", items_data=items_to_buy)

    assert "could not be validated" in str(exc_info.value)

def test_finish_sale_and_calculate_quotes_with_stunt_double():
    result = test_service.finish_sale(created_sale_id)
    
    finished_sale = result["sale"]
    prices = result["prices"]
    
    assert finished_sale.status == SaleStatus.DONE.value
    assert prices["BRL"] == 1000.00
    assert prices["USD"] == 200.00

def test_cleanup_test_database_at_the_end():
    db_path = "sales/database/db_test_sales.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    assert not os.path.exists(db_path)
