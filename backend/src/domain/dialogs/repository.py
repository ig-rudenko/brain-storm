from abc import ABC, abstractmethod
from uuid import UUID

from .entities import Dialog


class DialogRepository(ABC):
    """Интерфейс репозитория для Dialog."""

    @abstractmethod
    async def get_by_id(self, dialog_id: UUID) -> Dialog | None:
        pass

    @abstractmethod
    async def get_user_dialogs(self, user_id: UUID) -> list[Dialog]:
        pass

    @abstractmethod
    async def add(self, dialog: Dialog) -> Dialog:
        pass

    @abstractmethod
    async def update(self, dialog: Dialog) -> Dialog | None:
        pass

    @abstractmethod
    async def delete(self, dialog_id: UUID) -> None:
        pass
