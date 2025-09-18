from functools import cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dialogs.handlers import DialogHandler
from src.application.services import AgentLLMClient
from src.application.users.handlers import JWTObtainUserHandler
from src.infrastructure.db.base import get_session
from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.auth.hashers import BcryptPasswordHasher, PasswordHasherProtocol
from src.infrastructure.auth.token_service import JWTService
from src.infrastructure.llm.openai_client import OpenAIChatClient
from src.infrastructure.settings import settings


@cache
def get_hasher() -> PasswordHasherProtocol:
    return BcryptPasswordHasher()


@cache
def get_jwt_token_service() -> JWTService:
    return JWTService(
        secret=settings.jwt_secret,
        access_expiration_minutes=settings.jwt_access_token_expire_minutes,
        refresh_expiration_days=settings.jwt_refresh_token_expire_days,
    )


@cache
def get_llm() -> AgentLLMClient:
    return OpenAIChatClient(
        settings.openai_api_key,
        settings.openai_model_name,
    )


def get_login_handler(
    session: AsyncSession = Depends(get_session),
    hasher: BcryptPasswordHasher = Depends(get_hasher),
    token_service: JWTService = Depends(get_jwt_token_service),
) -> JWTObtainUserHandler:
    return JWTObtainUserHandler(uow=SqlAlchemyUnitOfWork(session), hasher=hasher, token_service=token_service)


def dialog_handler(
    session: AsyncSession = Depends(get_session, use_cache=True),
    llm: AgentLLMClient = Depends(get_llm),
):
    return DialogHandler(uow=SqlAlchemyUnitOfWork(session), llm=llm)
