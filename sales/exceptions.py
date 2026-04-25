class BaseError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

class DatabaseError(BaseError):
    def __init__(self, message: str = "A database operation failed."):
        super().__init__(message)

class SaleNotFound(BaseError):
    def __init__(self, sale_id: str):
        super().__init__(f"Sale with ID '{sale_id}' was not found.")

class InvalidSaleState(BaseError):
    def __init__(self, current_state: str, attempted_action: str):
        super().__init__(
            f"Cannot perform action '{attempted_action}' because the sale is currently '{current_state}'."
        )

class EmptySaleCannotBeCompleted(BaseError):
    def __init__(self, sale_id: str):
        super().__init__(f"Cannot complete sale '{sale_id}' because it has no products.")

class ExternalServiceUnavailable(BaseError):
    def __init__(self, service_name: str):
        super().__init__(f"The external service '{service_name}' is currently unavailable or not responding.")

class ClientIntegrationError(BaseError):
    def __init__(self, client_id: str):
        super().__init__(f"Client with ID '{client_id}' could not be validated in the Client Service.")

class ProductIntegrationError(BaseError):
    def __init__(self, product_id: str):
        super().__init__(f"Product with ID '{product_id}' could not be validated in the Product Service.")

class InsufficientStockIntegration(BaseError):
    def __init__(self, product_id: str, requested: int):
        super().__init__(
            f"Cannot add/update product '{product_id}'. "
            f"Requested quantity ({requested}) exceeds available stock in Product Service."
        )
