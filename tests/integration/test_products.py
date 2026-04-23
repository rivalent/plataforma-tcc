import requests
import time

BASE_URL = "http://127.0.0.1:8002"
UNIQUE_PRODUCT_NAME = f"Dragon Balls {int(time.time())}"

created_product_id = None

def test_create_product_successfully():
    global created_product_id

    payload = {
        "name": UNIQUE_PRODUCT_NAME,
        "desc": ".......",
        "price": 1000000.00,
        "quantity": 7
    }

    response = requests.post(f"{BASE_URL}/products", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data["message"] == "Product successfully created"

    created_product_id = data["data"]["id"]

def test_fetch_product_by_id_successfully():
    response = requests.get(f"{BASE_URL}/products/{created_product_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["data"]["id"] == created_product_id
    assert data["data"]["name"] == UNIQUE_PRODUCT_NAME.lower()

def test_search_products_by_name_successfully():
    response = requests.get(f"{BASE_URL}/products/search?name_or_desc=Dragon")
    data = response.json()
    
    assert response.status_code == 200

    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0

def test_update_product_details_successfully():
    payload = {
        "price": 10000000.00
    }
    
    response = requests.put(f"{BASE_URL}/products/{created_product_id}", json=payload)
    data = response.json()
    
    assert response.status_code == 200
    assert data["message"] == "Product updated successfully"
    assert data["data"]["price"] == 10000000.00

def test_update_product_stock_successfully():
    payload = {
        "quantity": 4
    }
    
    response = requests.put(f"{BASE_URL}/products/{created_product_id}/stock", json=payload)
    data = response.json()
    
    assert response.status_code == 200
    assert data["message"] == "Stock updated successfully via Integration."
    assert data["data"]["quantity"] == 4

def test_delete_product_logically():
    response = requests.delete(f"{BASE_URL}/products/{created_product_id}")
    
    assert response.status_code == 200

def test_return_404_when_fetching_deleted_product():
    response = requests.get(f"{BASE_URL}/products/{created_product_id}")
    
    assert response.status_code == 404
