from fastapi import FastAPI
from clients.api.client_api import router as client_router

app = FastAPI(title="Clients API")
app.include_router(client_router)
