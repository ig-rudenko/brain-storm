import re
from typing import Optional

from fastapi import Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services import get_user_by_token
from src.application.users.dto import UserDTO
from src.domain.common.exceptions import ValidationError
from src.infrastructure.auth.token_service import JWTService
from src.infrastructure.db.base import get_session
from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.api.dependencies import get_jwt_token_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session, use_cache=True),
    token_service: JWTService = Depends(get_jwt_token_service),
) -> UserDTO:
    """Получение текущего пользователя по токену аутентификации."""
    uow = SqlAlchemyUnitOfWork(session)

    try:
        user = await get_user_by_token(token, token_service=token_service, uow=uow)
    except (ValueError, ValidationError) as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return user


async def get_user_or_none(
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session, use_cache=True),
    token_service: JWTService = Depends(get_jwt_token_service),
) -> UserDTO | None:
    """
    Получение текущего пользователя по токену аутентификации.

    :param authorization: Значение заголовка HTTP (Authorization).
    :param session: :class:`AsyncSession` объект сессии.
    :param token_service: Объект сервиса для работы с токенами.
    :return: Объект пользователя :class:`User` или :class:`None`.
    :raises CredentialsException: Если пользователь не найден.
    """
    if authorization and (token_match := re.match(r"Bearer (\S+)", authorization)) is not None:
        try:
            return await get_current_user(token_match.group(1), session, token_service)
        except HTTPException:
            return None
    return None
