from abc import ABC, abstractmethod
from uuid import UUID
from .entities import User


class UserRepository(ABC):
    """Интерфейс репозитория для User."""

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[User]:
        pass

    @abstractmethod
    async def add(self, user: User) -> None:
        pass

    @abstractmethod
    async def update(self, user: User) -> None:
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass
