from repository.client_repository import ClientRepository
from clientes.domain.client_domain import ClientDomain
from datetime import date, datetime, timezone
from ulid import ULID
from exceptions import ClientAlreadyExists, InternalServerError, ClientNotFound
from config.logger_config import LoggerFactory

logger = LoggerFactory.get_logger("ClientServiceLogger")

class ClientService:
    def __init__(self, repo: ClientRepository):
        self.repo = repo
    
    def register_client(self, name: str, surname: str, email: str, birthdate: date) -> ClientDomain:
        try:
            logger.info("Starting client registration routine")

            email = email.replace(" ", "").strip().lower()
            
            logger.debug(f"Checking database for existing email: {email}")
            email_exists = self.repo.get_by_email(email)
            
            if email_exists:
                logger.warning(f"Routine interrupted: Email already registered ({email})")
                raise ClientAlreadyExists(email)

            client_id = str(ULID())
            created_at = datetime.now(timezone.utc)
            updated_at = datetime.now(timezone.utc)
            name = name.strip().lower()
            surname = surname.strip().lower()

            new_client = ClientDomain(
                id=client_id,
                name=name,
                surname=surname,
                email=email,
                birthdate=birthdate,
                created_at=created_at,
                updated_at=updated_at
            )

            self.repo.create(new_client)
            logger.info(f"Client registered successfully. Generated ID: {client_id}")
            
            return new_client
        
        except ClientAlreadyExists as e:
            raise e

        except Exception as e:
            logger.error(f"Internal failure while trying to register client: {str(e)}")
            raise InternalServerError

    def get_all_client(self):
        try:
            logger.info("Fetching all clients from the database")
            list_clients = self.repo.get_all()

            count = len(list_clients) if list_clients else 0
            logger.debug(f"Successfully retrieved {count} clients")
            
            return list_clients
        except Exception as e:
            logger.error(f"Internal failure while fetching all clients: {str(e)}")
            raise InternalServerError
    
    def get_client_by_id(self, client_id: str):
        try:
            client_id = client_id.replace(" ", "").strip()
            logger.info(f"Fetching client by ID: {client_id}")
            
            client = self.repo.get_by_id(client_id)

            if not client or not client.active:
                logger.debug(f"Client not found or is inactive for ID: {client_id}")
                return None
            
            logger.debug(f"Client successfully found for ID: {client_id}")
            return client

        except Exception as e:
            logger.error(f"Internal failure while fetching client by ID ({client_id}): {str(e)}")
            raise InternalServerError
    
    def get_client_by_email(self, email: str):
        try:
            email = email.replace(" ", "").strip().lower()
            logger.info(f"Fetching client by Email: {email}")
            
            client = self.repo.get_by_email(email)

            if not client or not client.active:
                logger.debug(f"Client not found or is inactive for Email: {email}")
                return None
            
            logger.debug(f"Client successfully found for Email: {email}")
            return client

        except Exception as e:
            logger.error(f"Internal failure while fetching client by Email ({email}): {str(e)}")
            raise InternalServerError
    
    def update_client(self, client_id: str, update_data: ClientDomain):
        try:
            client_id = client_id.replace(" ", "").strip()
            logger.info(f"Starting update routine for client ID: {client_id}")
            
            client = self.repo.get_by_id(client_id)

            if not client or not client.active:
                logger.warning(f"Update interrupted: Client not found or is inactive for ID ({client_id})")
                raise ClientNotFound(client_id)

            if update_data.name is not None:
                client.name = update_data.name.strip().lower()

            if update_data.surname is not None:
                client.surname = update_data.surname.strip().lower()

            if update_data.email is not None:
                new_email = update_data.email.replace(" ", "").strip().lower()

                logger.debug(f"Checking database for email collision: {new_email}")
                existing_client_with_email = self.repo.get_by_email(new_email)

                if existing_client_with_email and existing_client_with_email.id != client.id:
                    logger.warning(f"Update interrupted: Email already registered to another client ({new_email})")
                    raise ClientAlreadyExists(new_email)

                client.email = new_email

            if update_data.birthdate is not None:
                client.birthdate = update_data.birthdate

            client.updated_at = datetime.now(timezone.utc)

            self.repo.update(client)

            logger.info(f"Client updated successfully for ID: {client_id}")
            return client
        
        except ClientNotFound as e:
            raise e
            
        except ClientAlreadyExists as e:
            raise e

        except Exception as e:
            logger.error(f"Internal failure while updating client ({client_id}): {str(e)}")
            raise InternalServerError

    def delete_client(self, client_id: str):
        try:
            client_id = client_id.replace(" ", "").strip()
            logger.info(f"Starting logical deletion routine for client ID: {client_id}")
            
            client = self.repo.get_by_id(client_id)

            if not client or not client.active:
                logger.warning(f"Deletion interrupted: Client not found or already deleted for ID ({client_id})")
                raise ClientNotFound(client_id)

            client.active = False
            client.inactive_at = datetime.now(timezone.utc)
            client.updated_at = datetime.now(timezone.utc)

            self.repo.update(client)

            logger.info(f"Client logically deleted successfully. ID: {client_id}")
            return True

        except ClientNotFound as e:
            raise e

        except Exception as e:
            logger.error(f"Internal failure while deleting client ({client_id}): {str(e)}")
            raise InternalServerError
