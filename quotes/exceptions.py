class BaseError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class DatabaseError(BaseError):
    def __init__(self, message: str = "A database operation failed."):
        self.message = message
        super().__init__(self.message)

class QuoteServiceUnavailable(BaseError):
    def __init__(self, message: str = "The quote service is currently unavailable."):
        self.message = message
        super().__init__(self.message)