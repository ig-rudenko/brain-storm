from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.infrastructure.db.base import db_manager
from src.infrastructure.settings import settings
from src.presentation.api.controllers.auth import router as auth_router
from src.presentation.api.controllers.dialogs import router as dialogs_router


@asynccontextmanager
async def startup(app_instance: FastAPI):
    db_manager.init(settings.db_url)
    print("Database connected")
    yield
    await db_manager.close()
    print("Database disconnected")


app = FastAPI(lifespan=startup)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(dialogs_router, prefix="/api/v1")


@app.get("/ping", tags=["health"])
async def status():
    return {"message": "pong"}
