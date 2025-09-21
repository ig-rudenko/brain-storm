from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.infrastructure.db.base import db_manager
from src.infrastructure.settings import settings
from src.presentation.api.rest.agents import router as agents_rest_router
from src.presentation.api.rest.auth import router as auth_rest_router
from src.presentation.api.rest.dialogs import router as dialogs_rest_router
from src.presentation.api.rest.pipelines import router as pipelines_rest_router
from src.presentation.api.rpc.pipelines import router as pipelines_rpc_router


@asynccontextmanager
async def startup(app_instance: FastAPI):
    db_manager.init(settings.db_url)
    print("Database connected")
    yield
    await db_manager.close()
    print("Database disconnected")


app = FastAPI(lifespan=startup)

# RPC API
app.include_router(pipelines_rpc_router, prefix="/api/v1/rpc")

# REST API
app.include_router(auth_rest_router, prefix="/api/v1")
app.include_router(dialogs_rest_router, prefix="/api/v1")
app.include_router(agents_rest_router, prefix="/api/v1")
app.include_router(pipelines_rest_router, prefix="/api/v1")


@app.get("/ping", tags=["health"])
async def status():
    return {"message": "pong"}
