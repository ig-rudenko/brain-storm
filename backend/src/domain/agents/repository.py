from abc import ABC, abstractmethod
from uuid import UUID

from .entities import Agent


class AgentRepository(ABC):
    """Интерфейс репозитория для Agent."""

    @abstractmethod
    async def get_by_id(self, agent_id: UUID) -> Agent | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[Agent]:
        pass

    @abstractmethod
    async def add(self, agent: Agent) -> Agent:
        pass

    @abstractmethod
    async def update(self, agent: Agent) -> Agent | None:
        pass

    @abstractmethod
    async def delete(self, agent_id: UUID) -> None:
        pass
