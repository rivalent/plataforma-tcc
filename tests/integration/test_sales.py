import requests
import time

CLIENTS_BASE_URL = "http://127.0.0.1:8001"
PRODUCTS_BASE_URL = "http://127.0.0.1:8002"
SALES_BASE_URL = "http://127.0.0.1:8004"

created_client_id = None
created_product_id = None
created_sale_id = None

def test_setup_client_and_product_for_sale():
    global created_client_id, created_product_id

    client_payload = {
        "name": "Gon",
        "surname": "Freecss",
        "email": f"Gonfree{int(time.time())}@email.com",
        "birthdate": "2005-05-05"
    }
    client_resp = requests.post(f"{CLIENTS_BASE_URL}/clients", json=client_payload)
    assert client_resp.status_code == 201
    created_client_id = client_resp.json()["data"]["id"]

    product_payload = {
        "name": f"Greed Island {int(time.time())}",
        "desc": "Restores HP and Stamina",
        "price": 89000000.00,
        "quantity": 100
    }
    product_resp = requests.post(f"{PRODUCTS_BASE_URL}/products", json=product_payload)
    assert product_resp.status_code == 201
    created_product_id = product_resp.json()["data"]["id"]

def test_create_sale_successfully():
    global created_sale_id
    
    payload = {
        "client_id": created_client_id,
        "items": [
            {
                "product_id": created_product_id,
                "quantity": 3
            }
        ]
    }
    
    response = requests.post(f"{SALES_BASE_URL}/sales", json=payload)
    data = response.json()
    
    assert response.status_code == 201
    assert data["message"] == "Sale successfully created"
    assert data["data"]["status"] == 0
    
    created_sale_id = data["data"]["id"]

def test_finish_sale_and_deduct_stock():
    response = requests.put(f"{SALES_BASE_URL}/sales/{created_sale_id}/finish")
    data = response.json()
    
    assert response.status_code == 200
    assert data["data"]["sale"]["status"] == 2
    assert "prices" in data["data"]
    assert "BRL" in data["data"]["prices"]
    assert "USD" in data["data"]["prices"]

    product_resp = requests.get(f"{PRODUCTS_BASE_URL}/products/{created_product_id}")
    product_data = product_resp.json()

    assert product_data["data"]["quantity"] == 97

def test_cancel_sale_and_return_stock():
    response = requests.put(f"{SALES_BASE_URL}/sales/{created_sale_id}/cancel")
    data = response.json()
    
    assert response.status_code == 200
    assert data["data"]["status"] == 3

    product_resp = requests.get(f"{PRODUCTS_BASE_URL}/products/{created_product_id}")
    product_data = product_resp.json()
    
    assert product_data["data"]["quantity"] == 100