from fastapi import FastAPI
from sales.api.sale_api import router as sale_router

app = FastAPI(title="Sales API")
app.include_router(sale_router)