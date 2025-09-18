from abc import ABC, abstractmethod
from uuid import UUID
from .entities import Message


class MessageRepository(ABC):
    """Интерфейс репозитория для Message."""

    @abstractmethod
    async def get_by_id(self, message_id: UUID) -> Message | None:
        pass

    @abstractmethod
    async def get_by_dialog_id(self, dialog_id: UUID, limit: int = 10, offset: int = 0) -> list[Message]:
        pass

    @abstractmethod
    async def add(self, message: Message) -> Message:
        pass

    @abstractmethod
    async def update(self, message: Message) -> Message | None:
        pass

    @abstractmethod
    async def delete(self, message_id: UUID) -> None:
        pass
