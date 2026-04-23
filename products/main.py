from fastapi import FastAPI
from products.api.product_api import router as product_router

app = FastAPI(title="Products API")
app.include_router(product_router)
