from sales.repository.sales_repository import SaleRepository
from sales.domain.sales_domain import SaleDomain, SaleItemDomain, SaleStatus
from sales.gateway.api_gateway import APIGateway
from sales.exceptions import (
    SaleNotFound, InvalidSaleState, EmptySaleCannotBeCompleted,
    ProductIntegrationError, InsufficientStockIntegration, 
    ExternalServiceUnavailable, DatabaseError
)
from shared.logger_config import LoggerFactory
from datetime import datetime, timezone
from ulid import ULID

logger = LoggerFactory.get_logger("SalesServiceLogger")

class SalesService:
    def __init__(self, repo: SaleRepository, gateway: APIGateway):
        self.repo = repo
        self.gateway = gateway
    
    def save_sale(self, client_id: str, items_data: list[dict]) -> SaleDomain:
        try:
            logger.info("Starting sale saving routine")
            
            client_data = self.gateway.get_client(client_id)
            if not client_data:
                logger.warning(f"Sale rejected: Client {client_id} not found via API")
                raise Exception(f"Client {client_id} does not exist or is inactive.")
            
            domain_items = []
            sale_id = str(ULID())
            created_at = datetime.now(timezone.utc)
            updated_at = datetime.now(timezone.utc)
            
            for item in items_data:
                product_id = item["product_id"]
                requested_qty = item["quantity"]
                
                product_data = self.gateway.get_product(product_id)
                
                if not product_data:
                    logger.warning(f"Sale rejected: Product {product_id} not found via API")
                    raise Exception(f"Product {product_id} does not exist.")
                
                available_qty = product_data["quantity"]
                if requested_qty > available_qty:
                    logger.warning(f"Sale rejected: Insufficient stock for {product_id}. Requested: {requested_qty}, Available: {available_qty}")
                    raise Exception(f"Insufficient stock for product {product_id}.")
                
                domain_items.append(SaleItemDomain(
                    sell_id=sale_id,
                    product_id=product_id,
                    quantity=requested_qty,
                    created_at=created_at,
                    updated_at=updated_at
                ))

            logger.debug(f"All validations passed. Prepared sale data for ID: {sale_id}")

            new_sale = SaleDomain(
                id=sale_id,
                client_id=client_id,
                status=SaleStatus.STARTED.value,
                items=domain_items,
                created_at=created_at,
                updated_at=updated_at
            )

            saved_sale = self.repo.save(new_sale)
            logger.info(f"Sale saved successfully. ID: {sale_id}")
            
            return saved_sale

        except DatabaseError as e:
            raise e
        except Exception as e:
            logger.error(f"Internal failure while saving sale: {str(e)}")
            raise e
    
    def get_sale_by_id(self, sale_id: str) -> SaleDomain:
        try:
            logger.info(f"Fetching sale by ID: {sale_id}")
            sale = self.repo.get_by_id(sale_id)

            if not sale:
                logger.warning(f"Sale not found for ID: {sale_id}")
                raise SaleNotFound(sale_id)

            logger.info(f"Sale fetched successfully for ID: {sale_id}")
            return sale

        except SaleNotFound as e:
            raise e
        except DatabaseError as e:
            raise e
        except Exception as e:
            logger.error(f"Internal failure while fetching sale by ID ({sale_id}): {str(e)}")
            raise DatabaseError("Failed to fetch sale by ID from database.")
    
    def get_sale_by_product_id(self, product_id: str) -> list[SaleDomain]:
        try:
            logger.info(f"Fetching sales by Product ID: {product_id}")
            sales = self.repo.get_by_product(product_id)

            if not sales:
                logger.warning(f"No sales found for Product ID: {product_id}")
                return []

            count = len(sales)
            logger.info(f"Sales fetched successfully for Product ID: {product_id}. Found {count} sales.")
            return sales

        except DatabaseError as e:
            raise e
        except Exception as e:
            logger.error(f"Internal failure while fetching sales by Product ID ({product_id}): {str(e)}")
            raise DatabaseError("Failed to fetch sales by Product ID from database.")
    
    def get_sale_by_status(self, status: int) -> list[SaleDomain]:
        try:
            logger.info(f"Fetching sales by status: {status}")
            sales = self.repo.get_by_status(status)

            if not sales:
                logger.warning(f"No sales found for status: {status}")
                return []

            count = len(sales)
            logger.info(f"Sales fetched successfully for status: {status}. Found {count} sales.")
            return sales

        except DatabaseError as e:
            raise e
        except Exception as e:
            logger.error(f"Internal failure while fetching sales by status ({status}): {str(e)}")
            raise DatabaseError("Failed to fetch sales by status from database.")
    
    def count_sales_by_product_and_status(self, product_id: str, status: int) -> int:
        try:
            logger.info(f"Counting sales for Product ID: {product_id} and status: {status}")
            count = self.repo.count_by_product_and_status(product_id, status)
            logger.info(f"Counted {count} sales for Product ID: {product_id} and status: {status}")
            return count

        except DatabaseError as e:
            raise e
        except Exception as e:
            logger.error(f"Internal failure while counting sales by Product ID ({product_id}) and status ({status}): {str(e)}")
            raise DatabaseError("Failed to count sales by Product ID and status from database.")

    def finish_sale(self, sale_id: str) -> dict:
        try:
            sale_id = sale_id.replace(" ", "").strip()
            logger.info(f"Starting routine to finish sale: {sale_id}")
            sale = self.get_sale_by_id(sale_id)

            if sale.status != SaleStatus.STARTED.value:
                logger.warning(f"Routine interrupted: Sale {sale_id} is in '{sale.status}' state.")
                raise InvalidSaleState(sale.status, "finish_sale")

            if not sale.items:
                logger.warning(f"Routine interrupted: Sale {sale_id} has no items.")
                raise EmptySaleCannotBeCompleted(sale_id)

            products_to_update = []
            total_brl = 0.0

            for item in sale.items:
                product_data = self.gateway.get_product(item.product_id)
                
                if not product_data:
                    logger.warning(f"Product {item.product_id} not found via API.")
                    raise ProductIntegrationError(item.product_id)
                
                available_qty = product_data.get("quantity", 0)
                product_price = product_data.get("price", 0.0) 
                
                if item.quantity > available_qty:
                    logger.warning(f"Insufficient stock for {item.product_id}. Requested: {item.quantity}, Available: {available_qty}")
                    raise InsufficientStockIntegration(item.product_id, item.quantity)
                
                new_qty = available_qty - item.quantity
                products_to_update.append({"id": item.product_id, "new_qty": new_qty})

                total_brl += product_price * item.quantity
            
            for prod in products_to_update:
                self.gateway.update_product_stock(prod["id"], prod["new_qty"])

            sale.status = SaleStatus.DONE.value
            sale.updated_at = datetime.now(timezone.utc)
            
            finished_sale = self.repo.save(sale)

            prices_dict = {"BRL": round(total_brl, 2)}
            quotes = self.gateway.get_all_quotes()
            
            for q in quotes:
                quote_value = q.get("value", 0)
                if quote_value > 0:
                    prices_dict[q["code"]] = round(total_brl / quote_value, 2)

            logger.info(f"Sale {sale_id} finished successfully. Total: {total_brl} BRL")

            return {
                "sale": finished_sale,
                "prices": prices_dict
            }

        except (SaleNotFound, InvalidSaleState, EmptySaleCannotBeCompleted, 
                ProductIntegrationError, InsufficientStockIntegration, ExternalServiceUnavailable) as e:
            raise e
        except DatabaseError as e:
            raise e
        except Exception as e:
            logger.error(f"Internal failure while finishing sale ({sale_id}): {str(e)}")
            raise DatabaseError(f"Failed to finish sale.")
    
    def cancel_sale(self, sale_id: str) -> SaleDomain:
        try:
            sale_id = sale_id.replace(" ", "").strip()
            logger.info(f"Starting routine to cancel sale: {sale_id}")
            sale = self.get_sale_by_id(sale_id)

            if sale.status == SaleStatus.CANCELED.value:
                logger.warning(f"Routine interrupted: Sale {sale_id} is already canceled.")
                raise InvalidSaleState(sale.status, "cancel_sale")
            if sale.status == SaleStatus.DONE.value:
                logger.info(f"Sale {sale_id} was DONE. Returning stock to Products API.")
                
                for item in sale.items:
                    product_data = self.gateway.get_product(item.product_id)
                    
                    if product_data:
                        current_qty = product_data.get("quantity", 0)
                        new_qty = current_qty + item.quantity
                        self.gateway.update_product_stock(item.product_id, new_qty)
                    else:
                        logger.error(f"Could not return stock for product {item.product_id} because it was not found via API.")

            sale.status = SaleStatus.CANCELED.value
            sale.updated_at = datetime.now(timezone.utc)
            
            canceled_sale = self.repo.save(sale)

            logger.info(f"Sale {sale_id} canceled successfully.")
            return canceled_sale

        except (SaleNotFound, InvalidSaleState) as e:
            raise e
        except DatabaseError as e:
            raise e
        except Exception as e:
            logger.error(f"Internal failure while canceling sale ({sale_id}): {str(e)}")
            raise DatabaseError(f"Failed to cancel sale.")