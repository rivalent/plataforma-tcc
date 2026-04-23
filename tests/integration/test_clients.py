import requests
import time

BASE_URL = "http://127.0.0.1:8001"

UNIQUE_EMAIL = f"test.user.{int(time.time())}@rmail.com"

created_client_id = None

def test_return_success_when_fetching_client_list():
    response = requests.get(f"{BASE_URL}/clients")
    data = response.json()
    
    assert response.status_code == 200
    assert "data" in data

def test_create_client_successfully():
    global created_client_id
    
    payload = {
        "name": "Anna",
        "surname": "Liebert",
        "email": UNIQUE_EMAIL, 
        "birthdate": "1975-04-07"
    }
    
    response = requests.post(f"{BASE_URL}/clients", json=payload)
    data = response.json()
    
    assert response.status_code == 201
    assert data["message"] == "Client successfully registered"
    
    created_client_id = data["data"]["id"]

def test_reject_client_with_duplicated_email():
    payload = {
        "name": "Kenzo",
        "surname": "Tenma",
        "email": UNIQUE_EMAIL,
        "birthdate": "1958-01-02"
    }
    
    response = requests.post(f"{BASE_URL}/clients", json=payload)
    
    assert response.status_code == 409

def test_fetch_client_by_id_successfully():
    response = requests.get(f"{BASE_URL}/clients/{created_client_id}")
    data = response.json()
    
    assert response.status_code == 200
    assert data["data"]["id"] == created_client_id

def test_fetch_client_by_email_successfully():
    response = requests.get(f"{BASE_URL}/clients/email/{UNIQUE_EMAIL}")
    data = response.json()
    
    assert response.status_code == 200
    assert data["data"]["email"] == UNIQUE_EMAIL

def test_update_client_name_successfully():
    payload = {
        "name": "Johan"
    }
    
    response = requests.put(f"{BASE_URL}/clients/{created_client_id}", json=payload)
    data = response.json()
    
    assert response.status_code == 200
    assert data["message"] == "Client successfully updated"

def test_delete_client_logically():
    response = requests.delete(f"{BASE_URL}/clients/{created_client_id}")
    
    assert response.status_code == 200

def test_return_404_when_fetching_deleted_client():
    response = requests.get(f"{BASE_URL}/clients/id/{created_client_id}")
    
    assert response.status_code == 404
