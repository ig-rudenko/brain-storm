from src.application.services import AgentLLMClient
from src.domain.common.unit_of_work import UnitOfWork
from src.domain.pipelines.entities import Pipeline


class PipelineHandler:

    def __init__(self, uow: UnitOfWork, llm: AgentLLMClient):
        self.uow = uow
        self.llm = llm

    async def handle_create_pipeline(self, pipeline: Pipeline) -> Pipeline:
        async with self.uow:
            return await self.uow.pipelines.add(pipeline)
