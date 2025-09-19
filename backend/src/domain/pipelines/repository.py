from abc import ABC, abstractmethod

from .entities import Pipeline


class PipelineRepository(ABC):
    @abstractmethod
    async def get(self, pipeline_id: str) -> Pipeline: ...

    @abstractmethod
    async def add(self, pipeline: Pipeline) -> Pipeline: ...

    @abstractmethod
    async def list(self) -> list[Pipeline]: ...

    @abstractmethod
    async def delete(self, pipeline_id: str) -> None: ...
