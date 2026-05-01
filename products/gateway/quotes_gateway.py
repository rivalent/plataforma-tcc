from products.exceptions import UnsupportedCurrency
from shared.logger_config import LoggerFactory
import requests

logger = LoggerFactory.get_logger("QuotesGatewayLogger")

class QuotesGateway:
    def __init__(self, quotes_service_url: str):
        self.quotes_service_url = quotes_service_url.rstrip('/')

    def get_all_quotes(self):
        try:
            logger.info("Fetching all currency quotes from quotes service")
            response = requests.get(f"{self.quotes_service_url}/quotes")
            response.raise_for_status()
            data = response.json()

            quotes = {}
            for quote in data.get('data', []):
                quotes[quote['code']] = quote['value']
            
            logger.debug(f"Retrieved quotes: {quotes}")
            return quotes

        except requests.RequestException as e:
            logger.error(f"Failed to fetch quotes: {str(e)}")
            raise e

    def get_quote(self, currency_code: str):
        try:
            logger.info(f"Fetching quote for currency: {currency_code}")
            response = requests.get(f"{self.quotes_service_url}/quotes/{currency_code}")

            if response.status_code == 404:
                logger.warning(f"Unsupported currency requested: {currency_code}")
                raise UnsupportedCurrency(currency_code)

            response.raise_for_status()
            data = response.json()
            quote = data.get('data', {})
            value = quote.get('value')

            if value is None:
                logger.warning(f"Quote response for {currency_code} did not contain a value")
                raise UnsupportedCurrency(currency_code)
            
            logger.debug(f"Retrieved quote for {currency_code}: {value}")
            return value

        except requests.HTTPError:
            raise UnsupportedCurrency(currency_code)
        except requests.RequestException as e:
            logger.error(f"Failed to fetch quote for {currency_code}: {str(e)}")
            raise e
