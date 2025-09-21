from abc import ABC, abstractmethod
from uuid import UUID

from .entities import Message


class MessageRepository(ABC):
    """Интерфейс репозитория для Message."""

    @abstractmethod
    async def get_by_id(self, message_id: UUID) -> Message: ...

    @abstractmethod
    async def get_by_dialog_id(
        self, dialog_id: UUID, page: int, page_size: int
    ) -> tuple[list[Message], int]: ...

    @abstractmethod
    async def add(self, message: Message) -> Message: ...

    @abstractmethod
    async def add_many(self, messages: list[Message]) -> list[Message]: ...

    @abstractmethod
    async def update(self, message: Message) -> Message: ...

    @abstractmethod
    async def delete(self, message_id: UUID) -> None: ...
