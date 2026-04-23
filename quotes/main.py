from fastapi import FastAPI
from quotes.api.quote_api import router as quote_router

app = FastAPI(title="Quotes API")
app.include_router(quote_router)