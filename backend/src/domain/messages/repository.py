from abc import ABC, abstractmethod
from uuid import UUID
from .entities import Message


class MessageRepository(ABC):
    """Интерфейс репозитория для Message."""

    @abstractmethod
    async def get_by_id(self, message_id: UUID) -> Message | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[Message]:
        pass

    @abstractmethod
    async def add(self, message: Message) -> None:
        pass

    @abstractmethod
    async def update(self, message: Message) -> None:
        pass

    @abstractmethod
    async def delete(self, message_id: UUID) -> None:
        pass
