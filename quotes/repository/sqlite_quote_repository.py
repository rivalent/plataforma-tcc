from quotes.domain.quote_domain import QuoteDomain
from quotes.exceptions import DatabaseError
from shared.database import SqliteManager
from shared.logger_config import LoggerFactory

logger = LoggerFactory.get_logger("QuoteRepositoryLogger")

class SqliteQuoteRepository:
    def __init__(self, conn: SqliteManager):
        self.conn = conn
    
    def create_tables(self):
        try:
            logger.info("Initializing database: Verifying/Creating quotes table")
            quotes_table_query = ("""
                CREATE TABLE IF NOT EXISTS quotes (
                    code VARCHAR(10) PRIMARY KEY,
                    value FLOAT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)

            self.conn.execute_ddl(quotes_table_query)
            logger.debug("Table 'quotes' verified/created successfully.")

        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise DatabaseError("Failed to initialize database tables.")

    def map_row_to_quote(self, row) -> QuoteDomain:
        return QuoteDomain (
            code = row["code"],
            value = row["value"],
            created_at = row["created_at"]
        )

    def get_by_code(self, code) -> QuoteDomain:
        try:
            logger.debug(f"Fetching quote by code from database: {code}")
            query = """
                SELECT code, value, created_at
                FROM quotes
                WHERE code = ?
            """
            params = (code,)
            result = self.conn.fetch_one(query, params)

            if result:
                return self.map_row_to_quote(result)
            
            return None

        except Exception as e:
            logger.error(f"Database error while fetching quote by code ({code}): {str(e)}")
            raise DatabaseError("Failed to fetch quote by code from database.")

    def save(self, quote: QuoteDomain) -> QuoteDomain:
        try:
            logger.debug(f"Inserting/updating quote in database: {quote.code}")
            query = """
                INSERT INTO quotes (code, value, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                    value = excluded.value,
                    created_at = excluded.created_at
            """
            params = (
                quote.code,
                quote.value,
                quote.created_at
            )

            self.conn.execute_write(query, params)
            return quote
        
        except Exception as e:
            logger.error(f"Database error while saving quote ({quote.code}): {str(e)}")
            raise DatabaseError("Failed to save quote in database.")
