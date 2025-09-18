from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from src.application.users.dto import UserDTO
from src.domain.common.exceptions import ValidationError
from src.domain.common.unit_of_work import UnitOfWork
from src.domain.messages.entities import Message
from src.infrastructure.auth.token_service import JWTService


class AgentLLMClient(ABC):
    """Контракт для любого LLM клиента (ChatGPT, Claude, Gemini...)."""

    @abstractmethod
    async def generate(self, system_prompt: str, messages: list[Message], **kwargs: Any) -> str:
        """Сгенерировать ответ на основе prompt и опционального контекста."""


async def get_user_by_token(token: str, *, token_service: JWTService, uow: UnitOfWork) -> UserDTO:
    user_id: UUID = token_service.get_user_id(token, "access")
    async with uow:
        user = await uow.users.get_by_id(user_id)
        if user is None:
            raise ValidationError(f"Пользователь с id {user_id} не найден.")

        return UserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
