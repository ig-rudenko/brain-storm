from uuid import UUID

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
