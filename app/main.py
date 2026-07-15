from fastapi import FastAPI

from sqlalchemy import text

from app.api.routes.deliveries import router as deliveries_router
from app.api.routes.endpoints import router as endpoints_router
from app.api.routes.ingest import router as ingest_router

from app.database.session import engine
from app.database.models import WebhookEndpoint

app = FastAPI(
    title="HookScope",
    version="0.1.0",
)

app.include_router(deliveries_router)
app.include_router(endpoints_router)
app.include_router(ingest_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


##Healthcheks
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/health/database")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"database": "connected"}