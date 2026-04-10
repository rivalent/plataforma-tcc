from fastapi import FastAPI
import uvicorn
from clients.api.client_api import router as client_router
from clients.config.database import SqliteManager
from clients.repository.sqlite_client_repository import SqliteClientRepository

app = FastAPI()
app.include_router(client_router, tags=["Clients"])

@app.get("/")
def home():
    return {"a": "b"}

def startup_db():
    print("Checking and initializing the database...")
    manager = SqliteManager()
    repo = SqliteClientRepository(manager)
    repo.create_tables()
    print("Ready-to-use database!")

if __name__ == "__main__":
    startup_db()
    uvicorn.run(app, host="127.0.0.1", port=8001)
