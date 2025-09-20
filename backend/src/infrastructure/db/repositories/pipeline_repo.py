from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.pipelines.entities import Pipeline
from src.domain.pipelines.repository import PipelineRepository

from ..models import PipelineModel
from .mixins import SqlAlchemyRepositoryMixin


class SqlAlchemyPipelineRepository(PipelineRepository, SqlAlchemyRepositoryMixin):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, pipeline_id: UUID) -> Pipeline | None:
        stmt = select(PipelineModel).where(PipelineModel.id == pipeline_id)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def add(self, pipeline: Pipeline) -> Pipeline:
        model = PipelineModel(
            id=pipeline.id,
            name=pipeline.name,
            description=pipeline.description,
            definition=pipeline.root.model_dump(mode="json"),
        )
        self.session.add(model)
        await self._flush_changes()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def list(self) -> list[Pipeline]:
        stmt = select(PipelineModel)
        result = await self.session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def delete(self, pipeline_id: UUID) -> None:
        stmt = delete(PipelineModel).where(PipelineModel.id == pipeline_id)
        await self.session.execute(stmt)
        await self._flush_changes()

    @staticmethod
    def _to_domain(model: PipelineModel) -> Pipeline:
        print(model.definition)
        return Pipeline.model_validate({"id": model.id, "name": model.name, "root": model.definition})
