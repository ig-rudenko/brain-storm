from uuid import UUID

import advanced_alchemy
from advanced_alchemy.filters import LimitOffset
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.common.exceptions import ObjectNotFoundError
from src.domain.pipelines.entities import Pipeline
from src.domain.pipelines.repository import PipelineRepository

from ..models import PipelineModel
from .mixins import SqlAlchemyRepositoryMixin


class SQLPipelineRepository(SQLAlchemyAsyncRepository[PipelineModel]):
    model_type = PipelineModel


class SqlAlchemyPipelineRepository(PipelineRepository, SqlAlchemyRepositoryMixin):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repo = SQLPipelineRepository(session=session, auto_commit=False, auto_refresh=True)

    async def get_by_id(self, pipeline_id: UUID) -> Pipeline:
        try:
            agent = await self._repo.get(pipeline_id)
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError(f"Pipeline with id {pipeline_id} not found") from exc
        return self._to_domain(agent)

    async def add(self, pipeline: Pipeline) -> Pipeline:
        model = self._to_model(pipeline)
        model = await self._repo.add(model)
        return self._to_domain(model)

    async def get_paginated(self, page: int, page_size: int) -> tuple[list[Pipeline], int]:
        offset = (page - 1) * page_size
        results, total = await self._repo.list_and_count(LimitOffset(offset=offset, limit=page_size))
        return [self._to_domain(r) for r in results], total

    async def update(self, pipeline: Pipeline) -> Pipeline:
        model = self._to_model(pipeline)
        try:
            model = await self._repo.update(model, attribute_names=["name", "description", "definition"])
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError(f"Pipeline with id {pipeline.id} not found") from exc
        return self._to_domain(model)

    async def delete(self, pipeline_id: UUID) -> None:
        try:
            await self._repo.delete(pipeline_id)
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError(f"Pipeline with id {pipeline_id} not found") from exc

    @staticmethod
    def _to_domain(model: PipelineModel) -> Pipeline:
        return Pipeline.model_validate(
            {"id": model.id, "name": model.name, "description": model.description, "root": model.definition}
        )

    @staticmethod
    def _to_model(pipeline: Pipeline) -> PipelineModel:
        return PipelineModel(
            id=pipeline.id,
            name=pipeline.name,
            description=pipeline.description,
            definition=pipeline.root.model_dump(mode="json"),
        )
