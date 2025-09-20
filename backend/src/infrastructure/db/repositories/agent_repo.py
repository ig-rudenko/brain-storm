from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.agents.entities import Agent
from src.domain.agents.repository import AgentRepository
from src.infrastructure.db.models import AgentModel

from .mixins import SqlAlchemyRepositoryMixin


class SqlAlchemyAgentRepository(AgentRepository, SqlAlchemyRepositoryMixin):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, agent_id: UUID) -> Agent | None:
        stmt = select(AgentModel).where(AgentModel.id == agent_id)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def list_all(self) -> list[Agent]:
        stmt = select(AgentModel)
        result = await self.session.execute(stmt)
        return [self._to_domain(r) for r in result.scalars().all()]

    async def get_many(self, agent_ids: list[UUID]) -> list[Agent]:
        stmt = select(AgentModel).where(AgentModel.id.in_(agent_ids))
        result = await self.session.execute(stmt)
        return [self._to_domain(r) for r in result.scalars().all()]

    async def add(self, agent: Agent) -> Agent:
        model = AgentModel(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            prompt=agent.prompt,
            temperature=agent.temperature,
        )
        self.session.add(model)
        await self._flush_changes()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(self, agent: Agent) -> Agent | None:
        stmt = select(AgentModel).where(AgentModel.id == agent.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            model.name = agent.name
            model.description = agent.description
            model.prompt = agent.prompt
            model.temperature = agent.temperature
            await self._flush_changes()
            await self.session.refresh(model)
            return self._to_domain(model)
        return None

    async def delete(self, agent_id: UUID) -> None:
        stmt = select(AgentModel).where(AgentModel.id == agent_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            await self.session.delete(model)
            await self._flush_changes()

    @staticmethod
    def _to_domain(model: AgentModel) -> Agent:
        return Agent(
            id=model.id,
            name=model.name,
            description=model.description,
            prompt=model.prompt,
            temperature=model.temperature,
        )
