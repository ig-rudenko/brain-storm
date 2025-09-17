from abc import ABC, abstractmethod
from uuid import UUID
from .entities import Conversation


class ConversationRepository(ABC):
    """Интерфейс репозитория для Conversation."""

    @abstractmethod
    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[Conversation]:
        pass

    @abstractmethod
    async def add(self, conversation: Conversation) -> None:
        pass

    @abstractmethod
    async def update(self, conversation: Conversation) -> None:
        pass

    @abstractmethod
    async def delete(self, conversation_id: UUID) -> None:
        pass
