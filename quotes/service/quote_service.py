from quotes.repository.quote_repository import QuoteRepository
from quotes.domain.quote_domain import QuoteDomain
from quotes.exceptions import DatabaseError, QuoteServiceUnavailable
from shared.logger_config import LoggerFactory
from datetime import datetime, timezone
import requests

logger = LoggerFactory.get_logger("QuoteServiceLogger")

class QuoteService:
    def __init__(self, repo: QuoteRepository):
        self.repo = repo

    def get_quote(self, code: str) -> QuoteDomain:
        try:
            code = code.replace(" ", "").strip().upper()
            logger.info(f"Starting quote retrieval routine for code: {code}")
 
            logger.debug(f"Querying database for existing cached quote: {code}")
            quote = self.repo.get_by_code(code)

            if quote:
                quote_date = None
                if isinstance(quote.created_at, datetime):
                    quote_date = quote.created_at.date()
                elif isinstance(quote.created_at, str):
                    quote_date = datetime.fromisoformat(quote.created_at.replace("Z", "+00:00")).date()

                today_date = datetime.now(timezone.utc).date()

                if quote_date == today_date:
                    logger.info(f"Quote for code {code} is up-to-date. Returning cached value.")
                    return quote
                else:
                    logger.info(f"Quote for code {code} is outdated. Fetching new value.")
            else:
                logger.info(f"No existing quote found for code {code}. Fetching new value.")

            updated_quote = self.fetch_and_update_quote(code)
            return updated_quote

        except DatabaseError as e:
            raise e
        
        except Exception as e:
            logger.error(f"Internal failure while retrieving quote for code {code}: {str(e)}")
            raise e

    def fetch_and_update_quote(self, code: str) -> QuoteDomain:
        try:
            code = code.replace(" ", "").strip().upper()
            logger.info(f"Initiating external API request to fetch live quote for: {code}")
            url = "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,GBP-BRL,CNY-BRL"
            
            logger.debug(f"Sending get request to Awesomeapi: {url}")
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                expected_currencies = ["USD", "EUR", "GBP", "CNY"]
                requested_quote = None 

                logger.debug(f"Parsing API response and caching currencies: {expected_currencies}")

                for current_currency in expected_currencies:
                    key = f"{current_currency}BRL"
                    if key in data:
                        value = float(data[key]["bid"])
                        new_quote = QuoteDomain(
                            code=current_currency, 
                            value=value, 
                            created_at=datetime.now(timezone.utc)
                        )

                        self.repo.save(new_quote)

                        if current_currency == code:
                            requested_quote = new_quote
                
                if requested_quote:
                    logger.info(f"Quotes fetched and cached successfully. Returning requested code: {code}")
                    return requested_quote

                logger.error(f"Requested currency {code} not found in parsed data.")
                raise QuoteServiceUnavailable(f"Currency {code} not found.")

            logger.error(f"External API failed with status code {response.status_code}. Response: {response.text}")
            raise QuoteServiceUnavailable("Quotes API returned an unexpected status code.")

        except QuoteServiceUnavailable as e:
            raise e

        except Exception as e:
            logger.error(f"Error while fetching quote from external API for code {code}: {str(e)}")
            raise QuoteServiceUnavailable("Failed to fetch quote from external API.")
