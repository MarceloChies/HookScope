from fastapi import FastAPI

from contextlib import asynccontextmanager

from sqlalchemy import text

from app.api.routes.endpoints import router as endpoints_router

from app.database.session import engine
from app.database.models import WebhookEndpoint
from app.database.session import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="HookScope",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(endpoints_router)

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