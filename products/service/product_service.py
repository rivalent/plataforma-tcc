from products.repository.product_repository import ProductRepository
from products.domain.product_domain import ProductDomain
from products.exceptions import ProductNotFound, DatabaseError
from shared.logger_config import LoggerFactory
from datetime import datetime, timezone
from ulid import ULID

logger = LoggerFactory.get_logger("ProductServiceLogger")

class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def create_product(self, name: str, desc: str, price: float, quantity: int):
        try:
            logger.info("Starting product creation routine")
            
            product_id = str(ULID())
            name = name.strip().lower()
            desc = desc.strip().lower()
            created_at = datetime.now(timezone.utc)
            updated_at = datetime.now(timezone.utc)
            price = round(price, 2)

            logger.debug(f"Prepared product data for ID: {product_id}")

            new_product = ProductDomain(
                id=product_id,
                name=name,
                desc=desc,
                price=price,
                quantity=quantity,
                created_at=created_at,
                updated_at=updated_at
            )

            self.repo.create(new_product)
            
            logger.info(f"Product created successfully. ID: {product_id}")
            return new_product

        except DatabaseError as e:
            raise e
        except Exception as e:
            logger.error(f"Internal failure while creating product: {str(e)}")
            raise e
    
    def search(self, min_price: float = None, max_price: float = None, name_or_desc: str = None, min_quantity: int = None) -> list[ProductDomain]:
        try:
            logger.info("Starting product search routine")
            
            min_price = round(min_price, 2) if min_price is not None else None
            max_price = round(max_price, 2) if max_price is not None else None
            name_or_desc = name_or_desc.strip().lower() if name_or_desc is not None else None
            min_quantity = min_quantity if min_quantity is not None else None

            logger.debug(f"Applying search filters - min_price: {min_price}, max_price: {max_price}, name_or_desc: {name_or_desc}, min_quantity: {min_quantity}")
            
            results = self.repo.search(min_price, max_price, name_or_desc, min_quantity)

            count = len(results) if results else 0
            logger.info(f"Product search completed. Found {count} items.")
            
            return results

        except DatabaseError as e:
            raise e
        except Exception as e:
            logger.error(f"Internal failure while searching products: {str(e)}")
            raise e
    
    def get_by_id(self, product_id: str):
        try:
            product_id = product_id.replace(" ", "").strip()
            logger.info(f"Fetching product by ID: {product_id}")
            
            product = self.repo.get_by_id(product_id)

            if not product or not product.active:
                logger.warning(f"Routine interrupted: Product not found or inactive ({product_id})")
                raise ProductNotFound(product_id)
            
            logger.debug(f"Product successfully retrieved: {product_id}")
            return product

        except ProductNotFound as e:
            raise e
        except DatabaseError as e:
            raise e
        except Exception as e:
            logger.error(f"Internal failure while fetching product by ID ({product_id}): {str(e)}")
            raise e

    def update_product(self, product_id: str, update_data: ProductDomain):
        try:
            product_id = product_id.replace(" ", "").strip()
            logger.info(f"Starting update routine for product ID: {product_id}")
            
            existing_product = self.repo.get_by_id(product_id)
            if not existing_product or not existing_product.active:
                logger.warning(f"Update interrupted: Product not found or inactive ({product_id})")
                raise ProductNotFound(product_id)
            
            logger.debug(f"Applying updates to product: {product_id}")
            
            if update_data.name is not None:
                existing_product.name = update_data.name.strip().lower()

            if update_data.desc is not None:
                existing_product.desc = update_data.desc.strip().lower()

            if update_data.price is not None:
                existing_product.price = round(update_data.price, 2)

            if update_data.quantity is not None:
                existing_product.quantity = update_data.quantity
            
            existing_product.updated_at = datetime.now(timezone.utc)
            self.repo.update(existing_product)
            
            logger.info(f"Product updated successfully: {product_id}")
            return existing_product

        except ProductNotFound as e:
            raise e
        except DatabaseError as e:
            raise e
        except Exception as e:
            logger.error(f"Internal failure while updating product ({product_id}): {str(e)}")
            raise e
    
    def delete_product(self, product_id: str):
        try:
            product_id = product_id.replace(" ", "").strip()
            logger.info(f"Starting logical deletion routine for product ID: {product_id}")
            
            existing_product = self.repo.get_by_id(product_id)
            if not existing_product or not existing_product.active:
                logger.warning(f"Deletion interrupted: Product not found or already deleted ({product_id})")
                raise ProductNotFound(product_id)

            existing_product.active = False
            existing_product.inactive_at = datetime.now(timezone.utc)
            existing_product.updated_at = datetime.now(timezone.utc)

            self.repo.update(existing_product)
            
            logger.info(f"Product logically deleted successfully: {product_id}")
            return True

        except ProductNotFound as e:
            raise e

        except DatabaseError as e:
            raise e

        except Exception as e:
            logger.error(f"Internal failure while deleting product ({product_id}): {str(e)}")
            raise e
