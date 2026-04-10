class BaseError(Exception):
    pass

class ClientAlreadyExists(BaseError):
    def __init__(self, email: str):
        self.message = f"Client with email '{email}' already exists."
        super().__init__(self.message)

class ClientNotFound(BaseError):
    def __init__(self, client_id: str):
        self.message = f"Client with ID '{client_id}' was not found."
        super().__init__(self.message)

class InternalServerError(BaseError):
    def __init__(self, message: str = "An unexpected internal error occurred."):
        self.message = message
        super().__init__(self.message)

class DatabaseError(BaseError):
    def __init__(self, message: str = "A database operation failed."):
        self.message = message
        super().__init__(self.message)