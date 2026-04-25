import sqlite3
from pathlib import Path
from shared.logger_config import LoggerFactory

logger = LoggerFactory.get_logger("SqliteManagerLogger")

class SqliteManager:
    def __init__(self, target_folder: str, db_name: str):
        self.db_path = Path(__file__).parent.parent / target_folder / db_name
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row 

        logger.debug(f"Opening SQLite connection to {self.db_path}")
        return conn
    
    def execute_ddl(self, query):
        try:
            with self.get_connection() as conn:
                conn.executescript(query)
                logger.info("Executed DDL statement successfully.")
                return True

        except Exception as e:
            logger.error(f"Error to execute DDL (table creation): {e}")
            raise e

    def fetch_all(self, query, params=None):
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params or ())
                rows = cursor.fetchall()
                logger.debug(f"Fetched {len(rows)} rows for query: {query}")
                return rows

        except Exception as e:
            logger.error(f"Error to execute fetch_all: {e}")
            raise e

    def fetch_one(self, query, params=None):
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params or ())
                row = cursor.fetchone()
                logger.debug(f"Fetched single row for query: {query}")
                return row

        except Exception as e:
            logger.error(f"Error to execute fetch_one: {e}")
            raise e

    def execute_write(self, query, params=None):
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params or ())
                conn.commit()

                logger.info(f"Executed write statement successfully. Last row id: {cursor.lastrowid}")
                return {
                    "rowcount": cursor.rowcount,
                    "lastrowid": cursor.lastrowid
                }

        except Exception as e:
            logger.error(f"Error to execute write: {e}")
            raise e
