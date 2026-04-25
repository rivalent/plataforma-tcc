from fastapi import FastAPI
from contextlib import asynccontextmanager
from quotes.api.quote_api import router as quote_router
from quotes.repository.sqlite_quote_repository import SqliteQuoteRepository
from shared.database import SqliteManager
from shared.logger_config import LoggerFactory

logger = LoggerFactory.get_logger("QuotesAppLogger")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Quotes service lifepan.")
    manager = SqliteManager("quotes/database", "db_quotes.db")
    repo = SqliteQuoteRepository(manager)
    repo.create_tables()
    logger.info("Quotes database initialization complete.")
    yield
    logger.info("Stopping Quotes service lifespan.")

app = FastAPI(title="Quotes API", lifespan=lifespan)
app.include_router(quote_router)

@app.get("/")
def health_check():
    logger.info("Quotes health-check")
    return {"status": "Quotes service up"}
