from clientes.domain.client_domain import ClientDomain
from typing import Protocol, Optional

class ClientRepository(Protocol):
    def create(self, client: ClientDomain) -> ClientDomain:
        pass

    def read(self, id: str) -> Optional[ClientDomain]:
        pass

    def update(self, id: str, client: ClientDomain) -> Optional[ClientDomain]:
        pass

    def delete(self, id: str) -> bool:
        pass
    
    def get_by_email(self, email: str) -> Optional[ClientDomain]:
        pass

    def get_by_id(self, id: str) -> Optional[ClientDomain]:
        pass

    def get_all(self) -> list[ClientDomain]:
        pass