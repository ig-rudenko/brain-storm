from functools import cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.agents.handlers import AgentCommandHandler
from src.application.dialogs.handlers import DialogHandler
from src.application.pipelines.handlers import PipelineHandler
from src.application.services import AgentLLMClient
from src.application.users.handlers import JWTHandler, RegisterUserHandler
from src.infrastructure.auth.hashers import BcryptPasswordHasher, PasswordHasherProtocol
from src.infrastructure.auth.token_service import JWTService
from src.infrastructure.db.base import get_session
from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.llm.openai_client import OpenAIChatClient
from src.infrastructure.settings import settings


@cache
def get_hasher() -> PasswordHasherProtocol:
    return BcryptPasswordHasher()


@cache
def get_jwt_token_service(
    session: AsyncSession = Depends(get_session, use_cache=True),
) -> JWTService:
    return JWTService(
        secret=settings.jwt_secret,
        access_expiration_minutes=settings.jwt_access_token_expire_minutes,
        refresh_expiration_days=settings.jwt_refresh_token_expire_days,
    )


@cache
def get_llm() -> AgentLLMClient:
    return OpenAIChatClient(
        settings.openai_api_key,
        settings.openai_model,
        settings.openai_base_url,
    )


def get_token_auth_handler(
    session: AsyncSession = Depends(get_session, use_cache=True),
    hasher: BcryptPasswordHasher = Depends(get_hasher),
    token_service: JWTService = Depends(get_jwt_token_service),
) -> JWTHandler:
    return JWTHandler(uow=SqlAlchemyUnitOfWork(session), hasher=hasher, token_service=token_service)


def get_register_handler(
    session: AsyncSession = Depends(get_session, use_cache=True),
    hasher: BcryptPasswordHasher = Depends(get_hasher),
) -> RegisterUserHandler:
    return RegisterUserHandler(uow=SqlAlchemyUnitOfWork(session), hasher=hasher)


def get_agent_handler(
    session: AsyncSession = Depends(get_session, use_cache=True),
) -> AgentCommandHandler:
    return AgentCommandHandler(uow=SqlAlchemyUnitOfWork(session))


def get_dialog_handler(
    session: AsyncSession = Depends(get_session, use_cache=True),
    llm: AgentLLMClient = Depends(get_llm),
) -> DialogHandler:
    return DialogHandler(uow=SqlAlchemyUnitOfWork(session), llm=llm)


def get_pipeline_handler(
    session: AsyncSession = Depends(get_session, use_cache=True),
    llm: AgentLLMClient = Depends(get_llm),
) -> PipelineHandler:
    return PipelineHandler(uow=SqlAlchemyUnitOfWork(session), llm=llm)
