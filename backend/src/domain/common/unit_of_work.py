from abc import ABC, abstractmethod

from ..agents.repository import AgentRepository
from ..dialogs.repository import DialogRepository
from ..messages.repository import MessageRepository
from ..users.repository import UserRepository


class UnitOfWork(ABC):
    """Контракт для Unit of Work."""

    agents: "AgentRepository"
    users: "UserRepository"
    dialogs: "DialogRepository"
    messages: "MessageRepository"

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...
