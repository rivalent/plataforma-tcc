from sales.domain.sales_domain import SaleDomain, SaleItemDomain
from sales.exceptions import DatabaseError
from shared.database import SqliteManager
from shared.logger_config import LoggerFactory
from typing import Optional, List

logger = LoggerFactory.get_logger("SqliteSalesRepositoryLogger")

class SqliteSalesRepository:
    def __init__(self, conn: SqliteManager):
        self.conn = conn

    def create_tables(self):
        try:
            logger.info("Initializing database: Verifying/Creating sales table")
            sales_table_query = ("""
                CREATE TABLE IF NOT EXISTS sales (
                    id CHAR(26) PRIMARY KEY,
                    client_id CHAR(26) NOT NULL,
                    status INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)

            logger.info("Initializing database: Verifying/Creating sale_items table")
            sales_items_table_query = ("""
                CREATE TABLE IF NOT EXISTS sale_items (
                    sell_id CHAR(26) NOT NULL,
                    product_id CHAR(26) NOT NULL,
                    quantity INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (sell_id, product_id),
                    FOREIGN KEY (sell_id) REFERENCES sales(id)
                );
            """)

            self.conn.execute_ddl(sales_table_query)
            self.conn.execute_ddl(sales_items_table_query)
            logger.debug("Table 'sales' verified/created successfully.")
            logger.debug("Table 'sale_items' verified/created successfully.")
            
        
        except DatabaseError as e:
            logger.error(f"Database error during table creation: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during table creation: {str(e)}")
            raise DatabaseError("Failed to initialize database tables.")
    
    def map_item_to_row(self, row) -> SaleItemDomain:
        return SaleItemDomain(
            sell_id = row["sell_id"],
            product_id = row["product_id"],
            quantity = row["quantity"],
            created_at = row["created_at"],
            updated_at = row["updated_at"]
        )
    
    def map_sale_to_row(self, row, items: List[SaleItemDomain]) -> SaleDomain:
        return SaleDomain(
            id = row["id"],
            client_id = row["client_id"],
            status = row["status"],
            items = items,
            created_at = row["created_at"],
            updated_at = row["updated_at"]
        )

    def get_by_id(self, sale_id: str) -> Optional[SaleDomain]:
        try:
            sale_query = """
                SELECT id, client_id, status, created_at, updated_at
                FROM sales
                WHERE id = ?
            """
            sale_params = (sale_id,)
            sale_row = self.conn.fetch_one(sale_query, sale_params)

            if not sale_row:
                return None

            items_query = """
                SELECT sell_id, product_id, quantity, created_at, updated_at
                from sale_items
                WHERE sell_id = ?
            """
            items_params = (sale_id,)
            items_rows = self.conn.fetch_all(items_query, items_params)

            items_list = [self.map_item_to_row(row) for row in items_rows]
            return self.map_sale_to_row(sale_row, items_list)

        except DatabaseError as e:
            logger.error(f"Database error while fetching sale by ID ({sale_id}): {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error while fetching sale by ID ({sale_id}): {str(e)}")
            raise DatabaseError("Failed to fetch sale by ID from database.")
            
    
    def save(self, sale: SaleDomain) -> SaleDomain:
        try:
            sale_query = """
                INSERT INTO sales (id, client_id, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    updated_at = excluded.updated_at
            """
            sale_params = (
                sale.id,
                sale.client_id,
                sale.status,
                sale.created_at,
                sale.updated_at
            )
            self.conn.execute_write(sale_query, sale_params)

            item_query = """
                INSERT INTO sale_items (sell_id, product_id, quantity, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(sell_id, product_id) DO UPDATE SET
                    quantity = excluded.quantity,
                    updated_at = excluded.updated_at
            """
            
            for item in sale.items:
                item_params = (
                    item.sell_id,
                    item.product_id,
                    item.quantity,
                    item.created_at,
                    item.updated_at
                )
                self.conn.execute_write(item_query, item_params)
            
            return sale

        except DatabaseError as e:
            logger.error(f"Database error while saving sale ({sale.id}): {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error while saving sale ({sale.id}): {str(e)}")
            raise DatabaseError("Failed to save sale to database.")
    
    def get_by_product(self, product_id: str) -> List[SaleDomain]:
        try:
            query = """
                SELECT s.id
                FROM sales s
                JOIN sale_items si ON s.id = si.sell_id
                WHERE si.product_id = ?
            """
            params = (product_id,)
            rows = self.conn.fetch_all(query, params)

            sales_list = []
            for row in rows:
                full_sale = self.get_by_id(row["id"])
                if full_sale:
                    sales_list.append(full_sale)
                    
            return sales_list

        except DatabaseError as e:
            logger.error(f"Database error while fetching sales by product ID ({product_id}): {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Database error while fetching sales by product ID ({product_id}): {str(e)}")
            raise DatabaseError("Failed to fetch sales by product")
    
    def get_by_status(self, status: int) -> list[SaleDomain]:
        try:
            query = """
                SELECT id 
                FROM sales 
                WHERE status = ?
            """
            params = (status,)
            rows = self.conn.fetch_all(query, params)
            
            sales_list = []
            
            for row in rows:
                sale = self.get_by_id(row["id"])

                if sale is not None:
                    sales_list.append(sale)
                    
            return sales_list

        except DatabaseError as e:
            logger.error(f"Database error while fetching sales by status ({status}): {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Database error while fetching sales by status ({status}): {str(e)}")
            raise DatabaseError("Failed to fetch sales by status")
    
    def count_by_product_and_status(self, product_id: str, status: int) -> int:
        try:
            query = """
                SELECT COUNT(1) as total
                FROM sales s
                JOIN sale_items si ON s.id = si.sell_id
                WHERE si.product_id = ? AND s.status = ?
            """
            params = (product_id, status)
            result = self.conn.fetch_one(query, params)
            return result["total"] if result else 0

        except DatabaseError as e:
            logger.error(f"Database error while counting sales by product ID ({product_id}) and status ({status}): {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error while counting sales by product ID ({product_id}) and status ({status}): {str(e)}")
            raise DatabaseError("Failed to count sales by product and status")
