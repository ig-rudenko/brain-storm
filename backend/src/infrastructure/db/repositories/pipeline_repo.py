from uuid import UUID

from advanced_alchemy.filters import LimitOffset
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.pipelines.entities import Pipeline
from src.domain.pipelines.repository import PipelineRepository

from ..exception_handler import wrap_sqlalchemy_exception
from ..models import PipelineModel


class SQLPipelineRepository(SQLAlchemyAsyncRepository[PipelineModel]):
    model_type = PipelineModel

    @property
    def dialect(self):
        return self._dialect.name


class SqlAlchemyPipelineRepository(PipelineRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repo = SQLPipelineRepository(
            session=session, auto_commit=False, auto_refresh=True, wrap_exceptions=False
        )

    async def get_by_id(self, pipeline_id: UUID) -> Pipeline:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            agent = await self._repo.get(pipeline_id)
        return self._to_domain(agent)

    async def add(self, pipeline: Pipeline) -> Pipeline:
        model = self._to_model(pipeline)
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.add(model)
        return self._to_domain(model)

    async def get_paginated(self, page: int, page_size: int) -> tuple[list[Pipeline], int]:
        offset = (page - 1) * page_size
        with wrap_sqlalchemy_exception(self._repo.dialect):
            results, total = await self._repo.list_and_count(LimitOffset(offset=offset, limit=page_size))
        return [self._to_domain(r) for r in results], total

    async def update(self, pipeline: Pipeline) -> Pipeline:
        model = self._to_model(pipeline)
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.update(model, attribute_names=["name", "description", "definition"])
        return self._to_domain(model)

    async def delete(self, pipeline_id: UUID) -> None:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            await self._repo.delete(pipeline_id)

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
