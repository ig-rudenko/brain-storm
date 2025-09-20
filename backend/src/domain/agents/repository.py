from abc import ABC, abstractmethod
from uuid import UUID

from .entities import Agent


class AgentRepository(ABC):
    """Интерфейс репозитория для Agent."""

    @abstractmethod
    async def get_by_id(self, agent_id: UUID) -> Agent | None: ...

    @abstractmethod
    async def list_all(self) -> list[Agent]: ...

    @abstractmethod
    async def get_many(self, agent_ids: list[UUID]) -> list[Agent]: ...

    @abstractmethod
    async def add(self, agent: Agent) -> Agent: ...

    @abstractmethod
    async def update(self, agent: Agent) -> Agent | None: ...

    @abstractmethod
    async def delete(self, agent_id: UUID) -> None: ...
