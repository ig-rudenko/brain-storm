from abc import ABC, abstractmethod
from uuid import UUID

from .entities import Agent, AgentFilter


class AgentRepository(ABC):
    """Интерфейс репозитория для Agent."""

    @abstractmethod
    async def get_by_id(self, agent_id: UUID) -> Agent: ...

    @abstractmethod
    async def get_filtered(self, filter_: AgentFilter) -> tuple[list[Agent], int]: ...

    @abstractmethod
    async def get_many(self, agent_ids: list[UUID]) -> list[Agent]: ...

    @abstractmethod
    async def add(self, agent: Agent) -> Agent: ...

    @abstractmethod
    async def update(self, agent: Agent) -> Agent: ...

    @abstractmethod
    async def delete(self, agent_id: UUID) -> None: ...
