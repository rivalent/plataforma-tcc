class BaseError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

class DatabaseError(BaseError):
    def __init__(self, message: str = "A database operation failed."):
        super().__init__(message)

class ProductNotFound(BaseError):
    def __init__(self, identifier: str):
        super().__init__(f"Product not found or inactive: {identifier}")
