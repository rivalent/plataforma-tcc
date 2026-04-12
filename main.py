from fastapi import FastAPI
from contextlib import asynccontextmanager
from clients.api.client_api import router as client_router
from clients.repository.sqlite_client_repository import SqliteClientRepository
from products.api.product_api import router as product_router
from products.repository.sqlite_product_repository import SqliteProductRepository
from quotes.api.quote_api import router as quote_router
from quotes.repository.sqlite_quote_repository import SqliteQuoteRepository
from shared.database import SqliteManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Checking and initializing the databases...")

    client_manager = SqliteManager("clients/database", "db_clients.db")
    client_repo = SqliteClientRepository(client_manager)
    client_repo.create_tables()

    product_manager = SqliteManager("products/database", "db_products.db")
    product_repo = SqliteProductRepository(product_manager)
    product_repo.create_tables()

    quote_manager = SqliteManager("quotes/database", "db_quotes.db")
    quote_repo = SqliteQuoteRepository(quote_manager)
    quote_repo.create_tables()

    print("Ready-to-use databases!")
    yield  

app = FastAPI(lifespan=lifespan)

app.include_router(client_router, tags=["Clients"])
app.include_router(product_router, tags=["Products"])
app.include_router(quote_router, tags=["Quotes"])

@app.get("/")
def home():
    return {"": "Lee, oh Lee, o que foi que eu fiz? Olha só para você, nem está consciente e continua se empenhando em mostrar para o mundo o que pode fazer."}
