from fastapi import FastAPI

from src.infrastructure.db.base import db_manager
from src.infrastructure.settings import settings
from src.presentation.api.controllers.dialogs import router as dialogs_router
from src.presentation.api.controllers.auth import router as auth_router

app = FastAPI()


async def startup():
    db_manager.init(settings.db_url)


app.include_router(auth_router, prefix="/api/v1")
app.include_router(dialogs_router, prefix="/api/v1")
