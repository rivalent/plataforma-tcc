from shared.database import SqliteManager
from clients.domain.client_domain import ClientDomain
from clients.exceptions import DatabaseError
from shared.logger_config import LoggerFactory

logger = LoggerFactory.get_logger("ClientRepositoryLogger")

class SqliteClientRepository:
    def __init__(self, conn: SqliteManager):
        self.conn = conn

    def create_tables(self):
        try:
            logger.info("Initializing database: Verifying/Creating clients table")
            clients_table_query = ("""
                CREATE TABLE IF NOT EXISTS clients (
                    id CHAR(26) PRIMARY KEY,
                    name VARCHAR(256) NOT NULL,
                    surname VARCHAR(256) NOT NULL,
                    email  VARCHAR(512) NOT NULL,
                    birthdate DATE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    inactive_at DATETIME,
                    active BOOLEAN DEFAULT TRUE
                );
            """)

            self.conn.execute_ddl(clients_table_query)
            logger.debug("Table 'clients' verified/created successfully.")
            
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise DatabaseError("Failed to initialize database tables.")

    def map_row_to_client(self, row) -> ClientDomain:
        return ClientDomain (
            id = row["id"],
            name = row["name"],
            surname = row["surname"],
            email = row["email"],
            birthdate = row["birthdate"],
            created_at = row["created_at"],
            updated_at = row["updated_at"],
            inactive_at = row["inactive_at"],
            active = row["active"]
        )

    def create(self, client: ClientDomain):
        try:
            logger.debug(f"Inserting new client into database: {client.id}")
            query = """
                INSERT INTO clients (id, name, surname, email, birthdate, created_at, updated_at, inactive_at, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                client.id,
                client.name,
                client.surname,
                client.email,
                client.birthdate,
                client.created_at,
                client.updated_at,
                client.inactive_at,
                client.active
            )

            self.conn.execute_write(query, params)
            return client

        except Exception as e:
            logger.error(f"Database error while creating client ({client.id}): {str(e)}")
            raise DatabaseError("Failed to insert client into database.")

    def get_all(self) -> list[ClientDomain]:
        try:
            logger.debug("Executing query to fetch all clients")
            query = """
                SELECT id, name, surname, email, birthdate, created_at, updated_at, inactive_at, active
                FROM clients
            """
            result = self.conn.fetch_all(query)
            clients_list = []

            if result:
                for row in result:
                    clients_list.append(self.map_row_to_client(row))

            return clients_list

        except Exception as e:
            logger.error(f"Database error while fetching all clients: {str(e)}")
            raise DatabaseError("Failed to fetch clients from database.")

    def get_by_id(self, client_id) -> ClientDomain:
        try:
            logger.debug(f"Executing query to fetch client by ID: {client_id}")
            query = """
                SELECT id, name, surname, email, birthdate, created_at, updated_at, inactive_at, active
                FROM clients
                WHERE id = ? 
            """
            params = (client_id,)
            result = self.conn.fetch_one(query, params)

            if result:
                return self.map_row_to_client(result)
            
            return None

        except Exception as e:
            logger.error(f"Database error while fetching client by ID ({client_id}): {str(e)}")
            raise DatabaseError("Failed to fetch client by ID from database.")

    def get_by_email(self, client_email) -> ClientDomain:
        try:
            logger.debug(f"Executing query to fetch client by Email: {client_email}")
            query = """
                SELECT id, name, surname, email, birthdate, created_at, updated_at, inactive_at, active
                FROM clients
                WHERE email = ?
            """
            params = (client_email,)
            result = self.conn.fetch_one(query, params)

            if result:
                return self.map_row_to_client(result)
            
            return None

        except Exception as e:
            logger.error(f"Database error while fetching client by Email ({client_email}): {str(e)}")
            raise DatabaseError("Failed to fetch client by email from database.")

    def update(self, client: ClientDomain):
        try:
            logger.debug(f"Executing query to update client: {client.id}")
            
            if client.active:
                client.inactive_at = None
            
            query = """
                UPDATE clients
                SET name = ?, surname = ?, email = ?, birthdate = ?, updated_at = ?, active = ?, inactive_at = ?
                WHERE id = ?
            """
            params = (
                client.name,
                client.surname,
                client.email,
                client.birthdate,
                client.updated_at,
                client.active,
                client.inactive_at,
                client.id
            )

            self.conn.execute_write(query, params)
            return client

        except Exception as e:
            logger.error(f"Database error while updating client ({client.id}): {str(e)}")
            raise DatabaseError("Failed to update client in database.")
        
    def delete(self, client_id):
        try:
            logger.debug(f"Executing query to logically delete client: {client_id}")
            query = """
                UPDATE clients
                SET active = 0, inactive_at = datetime('now'), updated_at = datetime('now')
                WHERE id = ?
            """
            params = (client_id,)

            self.conn.execute_write(query, params)

        except Exception as e:
            logger.error(f"Database error while logically deleting client ({client_id}): {str(e)}")
            raise DatabaseError("Failed to delete client in database.")
