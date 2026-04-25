from fastapi import FastAPI
from contextlib import asynccontextmanager
from clients.api.client_api import router as client_router
from clients.repository.sqlite_client_repository import SqliteClientRepository
from shared.database import SqliteManager
from shared.logger_config import LoggerFactory

logger = LoggerFactory.get_logger("ClientsAppLogger")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Clients service.")
    manager = SqliteManager("clients/database", "db_clients.db")
    repo = SqliteClientRepository(manager)
    repo.create_tables()
    logger.info("Clients database initialization complete.")
    yield
    logger.info("Stopping Clients service lifespan.")

app = FastAPI(title="Clients API", lifespan=lifespan)
app.include_router(client_router)

@app.get("/")
def health_check():
    logger.info("Clients health-check")
    return {"status": "Clients service up"}
