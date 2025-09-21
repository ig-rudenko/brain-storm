from abc import ABC, abstractmethod
from uuid import UUID

from .entities import Pipeline


class PipelineRepository(ABC):
    @abstractmethod
    async def get_by_id(self, pipeline_id: UUID) -> Pipeline: ...

    @abstractmethod
    async def add(self, pipeline: Pipeline) -> Pipeline: ...

    @abstractmethod
    async def get_paginated(self, page: int, page_size: int) -> tuple[list[Pipeline], int]: ...

    @abstractmethod
    async def update(self, pipeline: Pipeline) -> Pipeline: ...

    @abstractmethod
    async def delete(self, pipeline_id: UUID) -> None: ...
