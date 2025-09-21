from uuid import UUID

from src.application.services import AgentLLMClient
from src.domain.agents.entities import Agent
from src.domain.common.unit_of_work import UnitOfWork
from src.domain.messages.entities import Message

from .commands import (
    CreateAgentCommand,
    PatchAgentPromptCommand,
    UpdateAgentPromptCommand,
)


class AgentCommandHandler:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def handle_create(self, cmd: CreateAgentCommand) -> Agent:
        agent = Agent.create(
            name=cmd.name,
            description=cmd.description,
            prompt=cmd.prompt,
            temperature=cmd.temperature,
        )
        async with self.uow:
            await self.uow.agents.add(agent)
        return agent

    async def handle_get(self, agent_id: UUID) -> Agent:
        agent = await self.uow.agents.get_by_id(agent_id)
        return agent

    async def handle_update(self, cmd: UpdateAgentPromptCommand) -> Agent:
        agent = Agent(
            id=cmd.agent_id,
            prompt=cmd.prompt,
            description=cmd.description,
            name=cmd.name,
            temperature=cmd.temperature,
        )
        async with self.uow:
            updated_agent = await self.uow.agents.update(agent)
        return updated_agent

    async def handle_patch(self, cmd: PatchAgentPromptCommand) -> Agent:
        agent = await self.uow.agents.get_by_id(cmd.agent_id)
        agent.patch(**cmd.model_dump())
        async with self.uow:
            updated_agent = await self.uow.agents.update(agent)
        return updated_agent

    async def handle_delete(self, agent_id: UUID) -> None:
        async with self.uow:
            await self.uow.agents.delete(agent_id)


class AgentRunner:

    def __init__(self, agent: Agent, llm_client: AgentLLMClient, dialog_id: UUID) -> None:
        self._dialog_id = dialog_id
        self._agent = agent
        self._llm_client = llm_client

    @property
    def agent(self) -> Agent:
        return self._agent

    @property
    def agent_id(self) -> UUID:
        return self._agent.id

    @property
    def llm_client(self) -> AgentLLMClient:
        return self._llm_client

    @property
    def dialog_id(self) -> UUID:
        return self._dialog_id

    async def run(self, messages: list[Message]) -> Message:
        """
        Запускает агента на выполнение. Видит только свои прошлые сообщения и сообщения пользователя.
        """
        answer: str = await self._llm_client.generate(
            system_prompt=self._agent.prompt,
            messages=messages,
        )
        print(f"Agent {self._agent.name} answer: {answer}, messages: {messages}")
        return Message.from_agent(dialog_id=self._dialog_id, agent_id=self._agent.id, text=answer)
