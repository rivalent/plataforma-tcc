import sqlite3
from pathlib import Path

class SqliteManager:
    def __init__(self, target_folder: str, db_name: str):
        self.db_path = Path(__file__).parent.parent / target_folder / db_name
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row 

        return conn
    
    def execute_ddl(self, query):
        try:
            with self.get_connection() as conn:
                conn.executescript(query)
                return True

        except Exception as e:
            print(f"Erro ao executar DDL (criação de tabela): {e}")
            raise e

    def fetch_all(self, query, params=None):
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params or ())
                return cursor.fetchall()

        except Exception as e:
            print(f"Erro ao executar fetch_all: {e}")
            raise e

    def fetch_one(self, query, params=None):
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params or ())
                return cursor.fetchone()

        except Exception as e:
            print(f"Erro ao executar fetch_one: {e}")
            raise e

    def execute_write(self, query, params=None):
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params or ())
                conn.commit()

                return {
                    "rowcount": cursor.rowcount,
                    "lastrowid": cursor.lastrowid
                }

        except Exception as e:
            print(f"Erro ao executar write: {e}")
            raise e
