from uuid import UUID

from src.application.services import AgentLLMClient
from src.domain.messages.entities import Message, AuthorType

from src.domain.agents.entities import Agent
from src.domain.agents.repository import AgentRepository

from .commands import CreateAgentCommand, UpdateAgentPromptCommand


class AgentCommandHandler:
    def __init__(self, repo: AgentRepository):
        self.repo = repo

    async def handle_create(self, cmd: CreateAgentCommand) -> Agent:
        agent = Agent.create(
            name=cmd.name,
            description=cmd.description,
            prompt=cmd.prompt,
            temperature=cmd.temperature,
        )
        await self.repo.add(agent)
        return agent

    async def handle_update_prompt(self, cmd: UpdateAgentPromptCommand) -> None:
        agent = await self.repo.get_by_id(UUID(cmd.agent_id))
        if not agent:
            raise ValueError("Agent not found")

        agent.update_prompt(cmd.new_prompt)
        await self.repo.update(agent)


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
