from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.pipelines.entities import Pipeline
from src.domain.pipelines.repository import PipelineRepository

from ..models import PipelineModel
from .mixins import SqlAlchemyRepositoryMixin


class SqlAlchemyPipelineRepository(PipelineRepository, SqlAlchemyRepositoryMixin):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, pipeline_id: str) -> Pipeline:
        stmt = select(PipelineModel).where(PipelineModel.id == pipeline_id)
        result = await self.session.execute(stmt)
        row = result.scalar_one()
        return self._to_domain(row)

    async def add(self, pipeline: Pipeline) -> Pipeline:
        model = PipelineModel(id=pipeline.id, name=pipeline.name, definition=pipeline.root.model_dump())
        self.session.add(model)
        await self._flush_changes()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def list(self) -> list[Pipeline]:
        stmt = select(PipelineModel)
        result = await self.session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def delete(self, pipeline_id: str) -> None:
        stmt = delete(PipelineModel).where(PipelineModel.id == pipeline_id)
        await self.session.execute(stmt)
        await self._flush_changes()

    @staticmethod
    def _to_domain(model: PipelineModel) -> Pipeline:
        return Pipeline.model_validate({"id": model.id, "name": model.name, "root": model.definition})
