from abc import ABC, abstractmethod

from ..agents.repository import AgentRepository
from ..auth.repository import RefreshTokenRepository
from ..dialogs.repository import DialogRepository
from ..messages.repository import MessageRepository
from ..pipelines.repository import PipelineRepository
from ..users.repository import UserRepository


class UnitOfWork(ABC):
    """Контракт для Unit of Work."""

    @property
    @abstractmethod
    def agents(self) -> AgentRepository: ...

    @property
    @abstractmethod
    def users(self) -> UserRepository: ...

    @property
    @abstractmethod
    def dialogs(self) -> DialogRepository: ...

    @property
    @abstractmethod
    def messages(self) -> MessageRepository: ...

    @property
    @abstractmethod
    def pipelines(self) -> PipelineRepository: ...

    @property
    @abstractmethod
    def refresh_token(self) -> RefreshTokenRepository: ...

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...
