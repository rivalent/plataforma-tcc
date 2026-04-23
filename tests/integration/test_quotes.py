import requests

BASE_URL = "http://127.0.0.1:8003"

def test_list_all_quotes_successfully():
    response = requests.get(f"{BASE_URL}/quotes")
    data = response.json()
    
    assert response.status_code == 200
    assert data["message"] == "All quotes retrieved successfully"
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0

    returned_currencies = [quote["code"] for quote in data["data"]]
    assert "USD" in returned_currencies
    assert "EUR" in returned_currencies

def test_fetch_dollar_quote_isolated():
    response = requests.get(f"{BASE_URL}/quotes/USD")
    data = response.json()
    
    assert response.status_code == 200
    assert data["message"] == "Quote retrieved successfully"
    assert data["data"]["code"] == "USD"
    assert "value" in data["data"]
    assert data["data"]["value"] > 0
