from fastapi import FastAPI
from contextlib import asynccontextmanager
from sales.api.sale_api import router as sale_router
from sales.repository.sqlite_sales_repository import SqliteSalesRepository
from shared.database import SqliteManager
from shared.logger_config import LoggerFactory

logger = LoggerFactory.get_logger("SalesAppLogger")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Sales service lifepan.")
    manager = SqliteManager("sales/database", "db_sales.db")
    repo = SqliteSalesRepository(manager)
    repo.create_tables()
    logger.info("Sales database initialization complete.")
    yield
    logger.info("Stopping Sales service lifespan.")

app = FastAPI(title="Sales API", lifespan=lifespan)
app.include_router(sale_router)

@app.get("/")
def health_check():
    logger.info("Sales health-check")
    return {"status": "Sales service up"}
