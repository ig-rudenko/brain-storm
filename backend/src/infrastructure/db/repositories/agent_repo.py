from uuid import UUID

import advanced_alchemy
from advanced_alchemy.filters import LimitOffset
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.agents.entities import Agent
from src.domain.agents.repository import AgentRepository
from src.domain.common.exceptions import ObjectNotFoundError
from src.infrastructure.db.models import AgentModel


class SQLAgentRepository(SQLAlchemyAsyncRepository[AgentModel]):
    model_type = AgentModel


class SqlAlchemyAgentRepository(AgentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repo = SQLAgentRepository(session=session, auto_commit=False, auto_refresh=True)

    async def get_by_id(self, agent_id: UUID) -> Agent:
        try:
            model = await self._repo.get(agent_id)
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError(f"Agent with id {agent_id} not found") from exc
        return self._to_domain(model)

    async def get_paginated(self, page: int, page_size: int) -> tuple[list[Agent], int]:
        offset = (page - 1) * page_size
        results, total = await self._repo.list_and_count(LimitOffset(offset=offset, limit=page_size))
        return [self._to_domain(r) for r in results], total

    async def get_many(self, agent_ids: list[UUID]) -> list[Agent]:
        results = await self._repo.list(AgentModel.id.in_(agent_ids))
        return [self._to_domain(r) for r in results]

    async def add(self, agent: Agent) -> Agent:
        model = self._to_model(agent)
        model = await self._repo.add(model)
        return self._to_domain(model)

    async def update(self, agent: Agent) -> Agent:
        model = self._to_model(agent)
        try:
            model = await self._repo.update(
                model, attribute_names=["name", "description", "prompt", "temperature"]
            )
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError(f"Agent with id {agent.id} not found") from exc
        return self._to_domain(model)

    async def delete(self, agent_id: UUID) -> None:
        try:
            await self._repo.delete(agent_id)
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError(f"Agent with id {agent_id} not found") from exc

    @staticmethod
    def _to_domain(model: AgentModel) -> Agent:
        return Agent(
            id=model.id,
            name=model.name,
            description=model.description,
            prompt=model.prompt,
            temperature=model.temperature,
        )

    @staticmethod
    def _to_model(agent: Agent) -> AgentModel:
        return AgentModel(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            prompt=agent.prompt,
            temperature=agent.temperature,
        )
