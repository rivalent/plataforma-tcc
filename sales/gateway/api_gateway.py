import requests
from shared.logger_config import LoggerFactory
from sales.exceptions import ExternalServiceUnavailable

logger = LoggerFactory.get_logger("SalesGatewayLogger")

class APIGateway:
    def __init__(self, 
                 clients_url: str = "http://clients-api:8000", 
                 products_url: str = "http://products-api:8000", 
                 quotes_url: str = "http://quotes-api:8000"
        ):
        self.clients_url = clients_url
        self.products_url = products_url
        self.quotes_url = quotes_url

    def get_client(self, client_id: str) -> dict:
        try:
            url = f"{self.clients_url}/clients/{client_id}"
            logger.info(f"Gateway: Requesting client data from {url}")
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json().get("data")
            if response.status_code == 404:
                return None
                
            logger.error(f"Unexpected status {response.status_code} from Clients API")
            raise ExternalServiceUnavailable("Clients API")
            
        except requests.RequestException as e:
            logger.error(f"HTTP Connection error to Clients API: {str(e)}")
            raise ExternalServiceUnavailable("Clients API")

    def get_product(self, product_id: str) -> dict:
        try:
            url = f"{self.products_url}/products/{product_id}"
            logger.info(f"Gateway: Requesting product data from {url}")

            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json().get("data")
            if response.status_code == 404:
                return None
                
            logger.error(f"Unexpected status {response.status_code} from Products API")
            raise ExternalServiceUnavailable("Products API")
            
        except requests.RequestException as e:
            logger.error(f"HTTP Connection error to Products API: {str(e)}")
            raise ExternalServiceUnavailable("Products API")
    
    def update_product_stock(self, product_id: str, new_quantity: int) -> bool:
        try:
            url = f"{self.products_url}/products/{product_id}/stock"
            logger.info(f"Gateway: Updating product stock via {url} with new quantity {new_quantity}")

            response = requests.put(url, json={"quantity": new_quantity}, timeout=5)
            
            if response.status_code == 200:
                return True
            if response.status_code == 404:
                logger.warning(f"Product {product_id} not found when attempting stock update")
                return False
            
            logger.error(f"Unexpected status {response.status_code} from Products API during stock update")
            raise ExternalServiceUnavailable("Products API")
            
        except requests.RequestException as e:
            logger.error(f"HTTP Connection error to Products API during stock update: {str(e)}")
            raise ExternalServiceUnavailable("Products API")

    def get_all_quotes(self) -> list:
        try:
            url = f"{self.quotes_url}/quotes"
            logger.info(f"Gateway: Requesting quotes data from {url}")
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json().get("data", [])
                
            logger.error(f"Unexpected status {response.status_code} from Quotes API")
            raise ExternalServiceUnavailable("Quotes API")
            
        except requests.RequestException as e:
            logger.error(f"HTTP Connection error to Quotes API: {str(e)}")
            raise ExternalServiceUnavailable("Quotes API")
