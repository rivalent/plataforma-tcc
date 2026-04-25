from products.api.product_api import router as product_router
from products.repository.sqlite_product_repository import SqliteProductRepository
from shared.database import SqliteManager
from shared.logger_config import LoggerFactory
from fastapi import FastAPI
from contextlib import asynccontextmanager

logger = LoggerFactory.get_logger("ProductsAppLogger")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Products service lifespan")
    manager = SqliteManager("products/database", "db_products.db")
    repo = SqliteProductRepository(manager)
    repo.create_tables()
    logger.info("Products database initialization complete")
    yield
    logger.info("Stopping Products service lifespan")

app = FastAPI(title="Products API", lifespan=lifespan)
app.include_router(product_router)

@app.get("/")
def health_check():
    logger.info("Products health-check")
    return {"status": "Products service up"}
