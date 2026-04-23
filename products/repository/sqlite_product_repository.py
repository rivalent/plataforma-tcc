from products.domain.product_domain import ProductDomain
from products.exceptions import DatabaseError
from shared.database import SqliteManager
from shared.logger_config import LoggerFactory
from typing import Optional
from datetime import datetime, timezone

logger = LoggerFactory.get_logger("ProductRepositoryLogger")

class SqliteProductRepository:
    def __init__(self, conn: SqliteManager):
        self.conn = conn

    def create_tables(self):
        try:
            logger.info("Initializing database: Verifying/Creating products table")
            products_table_query = ("""
                CREATE TABLE IF NOT EXISTS products (
                    id CHAR(26) PRIMARY KEY,
                    name VARCHAR(256) NOT NULL,
                    "desc" VARCHAR(1000) NOT NULL,
                    price FLOAT NOT NULL,
                    quantity INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    inactive_at DATETIME,
                    active BOOLEAN DEFAULT TRUE
                );
            """)

            self.conn.execute_ddl(products_table_query)
            logger.debug("Table 'products' verified/created successfully.")
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise DatabaseError("Failed to initialize database tables.")
    
    def map_row_to_product(self, row) -> ProductDomain:
        return ProductDomain (
            id = row["id"],
            name = row["name"],
            desc = row["desc"],
            price = row["price"],
            quantity = row["quantity"],
            created_at = row["created_at"],
            updated_at= row["updated_at"],
            inactive_at = row["inactive_at"],
            active = row["active"]
        )
    
    def create(self, product: ProductDomain):
        try:
            logger.debug(f"Inserting new product into database: {product.id}")
            query = """
                INSERT INTO products (id, name, "desc", price, quantity, created_at, updated_at, inactive_at, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                product.id,
                product.name,
                product.desc,
                product.price,
                product.quantity,
                product.created_at,
                product.updated_at,
                product.inactive_at,
                product.active
            )

            self.conn.execute_write(query, params)
            return product

        except Exception as e:
            logger.error(f"Database error while creating product ({product.id}): {str(e)}")
            raise DatabaseError("Failed to insert product into database.")
    
    def search(
            self, 
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            name_or_desc: Optional[str] = None,
            min_quantity: Optional[int] = None
        ) -> list[ProductDomain]:
        try:
            logger.debug("Executing dynamic search query for products")
            query = """
                SELECT id, name, "desc", price, quantity, created_at, updated_at, inactive_at, active
                FROM products
                WHERE active = 1
            """
            params = []

            if min_price is not None:
                query += " AND price >= ?"
                params.append(min_price)
            if max_price is not None:
                query += " AND price <= ?"
                params.append(max_price)
            
            if min_quantity is not None:
                query += " AND quantity >= ?"
                params.append(min_quantity)

            if name_or_desc is not None:
                query += ' AND (name LIKE ? OR "desc" LIKE ?)'
                params.append(f"%{name_or_desc}%")
                params.append(f"%{name_or_desc}%")
            
            rows = self.conn.fetch_all(query, tuple(params))
            products = [self.map_row_to_product(row) for row in rows]

            logger.debug(f"Search returned {len(products)} products")
            return products
        
        except Exception as e:
            logger.error(f"Database error while searching products: {str(e)}")
            raise DatabaseError("Failed to search products in database.")

    def get_by_id(self, product_id) -> ProductDomain:
        try:
            logger.debug(f"Executing query to fetch product by ID: {product_id}")
            query = """
                SELECT id, name, "desc", price, quantity, created_at, updated_at, inactive_at, active
                FROM products
                WHERE id = ? AND active = 1
            """
            params = (product_id,)
            result = self.conn.fetch_one(query, params)

            if result:
                return self.map_row_to_product(result)
            
            return None

        except Exception as e:
            logger.error(f"Database error while fetching product by ID ({product_id}): {str(e)}")
            raise DatabaseError("Failed to fetch product by ID from database.")
    
    def update(self, product: ProductDomain):
        try:
            logger.debug(f"Updating product in database: {product.id}")

            if product.active:
                product.inactive_at = None

            query = """
                UPDATE products
                SET name = ?, "desc" = ?, price = ?, quantity = ?, updated_at = ?, inactive_at = ?, active = ?
                WHERE id = ? AND active = 1
            """

            params = (
                product.name,
                product.desc,
                product.price,
                product.quantity,
                product.updated_at,
                product.inactive_at,
                product.active,
                product.id
            )

            self.conn.execute_write(query, params)
            return product

        except Exception as e:
            logger.error(f"Database error while updating product ({product.id}): {str(e)}")
            raise DatabaseError("Failed to update product in database.")
    
    def update_stock(self, product_id: str, new_quantity: int, updated_at: datetime):
        try:
            logger.debug(f"Updating stock for product {product_id} to new quantity: {new_quantity}")
            query = """
                UPDATE products
                SET quantity = ?, updated_at = ?
                WHERE id = ? AND active = 1
            """
            params = (new_quantity, updated_at, product_id)
            self.conn.execute_write(query, params)
            return True

        except Exception as e:
            logger.error(f"Database error while updating stock for product ({product_id}): {str(e)}")
            raise DatabaseError("Failed to update product stock in database.")

    def delete(self, product_id):
        try:
            logger.debug(f"Soft-deleting product in database: {product_id}")
            query = """
                UPDATE products
                SET active = 0, inactive_at = CURRENT_TIMESTAMP
                WHERE id = ? AND active = 1
            """
            params = (product_id,)
            self.conn.execute_write(query, params)

        except Exception as e:
            logger.error(f"Database error while deleting product ({product_id}): {str(e)}")
            raise DatabaseError("Failed to delete product from database.")
