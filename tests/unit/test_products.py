from products.service.product_service import ProductService
from products.repository.sqlite_product_repository import SqliteProductRepository
from products.domain.product_domain import ProductDomain
from products.exceptions import ProductNotFound
from shared.database import SqliteManager
import os
import time
import pytest

test_manager = SqliteManager("products/database", "db_test_products.db")
test_repo = SqliteProductRepository(test_manager)
test_repo.create_tables()
test_service = ProductService(test_repo)

UNIQUE_PRODUCT_NAME = f"odm gear {int(time.time())}"
created_product_id = None

def test_create_product():
    global created_product_id

    new_product = test_service.create_product(
        name=UNIQUE_PRODUCT_NAME,
        desc="Omni-directional mobility gear with ultra-hard steel blades",
        price=15000.50,
        quantity=104
    )

    assert new_product.id is not None
    assert new_product.name == UNIQUE_PRODUCT_NAME
    assert new_product.desc == "omni-directional mobility gear with ultra-hard steel blades"
    assert new_product.price == 15000.50
    assert new_product.quantity == 104
    assert new_product.active is True

    created_product_id = new_product.id

def test_fetch_product_by_id():
    fetched_product = test_service.get_by_id(created_product_id)

    assert fetched_product is not None
    assert fetched_product.id == created_product_id
    assert fetched_product.name == UNIQUE_PRODUCT_NAME

def test_search_products():
    results = test_service.search(name_or_desc="ultra-hard steel", min_quantity=50)

    assert isinstance(results, list)
    assert len(results) > 0
    found_ids = [product.id for product in results]
    assert created_product_id in found_ids

def test_update_product():
    update_data = ProductDomain(
        id=created_product_id, 
        name="Anti-Personnel ODM Gear",
        desc=None, 
        price=25000.00,
        quantity=None,
        created_at=None,
        updated_at=None
    )
    updated_product = test_service.update_product(created_product_id, update_data)

    assert updated_product.name == "anti-personnel odm gear"
    assert updated_product.price == 25000.00
    assert updated_product.quantity == 104
    assert updated_product.desc == "omni-directional mobility gear with ultra-hard steel blades"

def test_update_product_stock():
    updated_product = test_service.update_stock(created_product_id, new_quantity=89)

    assert updated_product.quantity == 89
    fetched_db_product = test_service.get_by_id(created_product_id)
    assert fetched_db_product.quantity == 89

def test_soft_delete_product():
    result = test_service.delete_product(created_product_id)
    assert result is True

def test_raise_exception_fetching_deleted_product():
    with pytest.raises(ProductNotFound):
        test_service.get_by_id(created_product_id)

def test_cleanup_test_databases():
    db_path = "products/database/db_test_products.db"
    
    if os.path.exists(db_path):
        os.remove(db_path)
    assert not os.path.exists(db_path)
