from abc import ABC, abstractmethod
from uuid import UUID

from .entities import Dialog


class DialogRepository(ABC):
    """Интерфейс репозитория для Dialog."""

    @abstractmethod
    async def get_by_id(self, dialog_id: UUID) -> Dialog: ...

    @abstractmethod
    async def get_user_dialogs(
        self, user_id: UUID, page: int, page_size: int
    ) -> tuple[list[Dialog], int]: ...

    @abstractmethod
    async def add(self, dialog: Dialog) -> Dialog: ...

    @abstractmethod
    async def update(self, dialog: Dialog) -> Dialog: ...

    @abstractmethod
    async def delete(self, dialog_id: UUID) -> None: ...
