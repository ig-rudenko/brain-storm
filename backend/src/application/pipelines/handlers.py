from uuid import UUID

from src.application.messages.dto import MessageDTO
from src.application.pipelines.commands import RunPipelineCommand
from src.application.pipelines.dto import PatchPipelineCommand
from src.application.services import AgentLLMClient
from src.domain.common.exceptions import ObjectNotFoundError
from src.domain.common.unit_of_work import UnitOfWork
from src.domain.pipelines.entities import Pipeline
from src.infrastructure.pipelines.executor import PipelineExecutor


class PipelineHandler:

    def __init__(self, uow: UnitOfWork, llm: AgentLLMClient):
        self.uow = uow
        self.llm = llm

    async def handle_create(self, pipeline: Pipeline) -> Pipeline:
        await self._check_pipeline(pipeline)
        async with self.uow:
            return await self.uow.pipelines.add(pipeline)

    async def handle_get(self, pipeline_id: UUID) -> Pipeline:
        async with self.uow:
            pipeline = await self.uow.pipelines.get_by_id(pipeline_id)
            return pipeline

    async def handle_update(self, pipeline: Pipeline) -> Pipeline:
        await self._check_pipeline(pipeline)
        async with self.uow:
            pipeline = await self.uow.pipelines.update(pipeline)
            return pipeline

    async def handle_patch(self, cmd: PatchPipelineCommand) -> Pipeline:
        pipeline = await self.uow.pipelines.get_by_id(cmd.pipeline_id)
        pipeline.patch(**cmd.to_dict())
        await self._check_pipeline(pipeline)
        async with self.uow:
            pipeline = await self.uow.pipelines.update(pipeline)
        return pipeline

    async def handle_delete(self, pipeline_id: UUID) -> None:
        async with self.uow:
            await self.uow.pipelines.delete(pipeline_id)

    async def handle_run_pipeline(self, cmd: RunPipelineCommand) -> list[MessageDTO]:
        async with self.uow:
            pipeline = await self.uow.pipelines.get_by_id(cmd.pipeline_id)
            dialog = await self.uow.dialogs.get_by_id(cmd.dialog_id)

            if dialog.user_id != cmd.user_id:
                raise ValueError(f"User with id {cmd.user_id} is not owner of dialog with id {cmd.dialog_id}")

            messages, _ = await self.uow.messages.get_by_dialog_id(cmd.dialog_id, page=1, page_size=100)
            await self._check_pipeline(pipeline)

            agents = await self.uow.agents.get_many(pipeline.get_agent_ids())
            executor = PipelineExecutor(pipeline, agents=agents, dialog_id=cmd.dialog_id, llm_client=self.llm)
            new_messages = await executor.run(
                user_id=cmd.user_id, history=messages, user_input=cmd.user_message
            )
            await self.uow.messages.add_many(executor.generated_messages)

        return [
            MessageDTO(
                id=msg.id,
                dialog_id=msg.dialog_id,
                text=msg.text,
                author_id=msg.author_id,
                author_type=msg.author_type,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
            )
            for msg in new_messages
        ]

    async def _check_pipeline(self, pipeline: Pipeline):
        if not pipeline.root:
            raise ValueError("Pipeline must have a root node")

        agents_id = pipeline.get_agent_ids()
        agents = await self.uow.agents.get_many(agents_id)
        existing_agents_id = [agent.id for agent in agents]
        if len(agents) != len(agents_id):
            for agent_id in agents_id:
                if agent_id not in existing_agents_id:
                    raise ObjectNotFoundError(f"Agent with id {agent_id} not found")
