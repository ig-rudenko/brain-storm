from uuid import UUID

from pydantic import BaseModel


class CreateAgentCommand(BaseModel):
    name: str
    description: str
    prompt: str
    temperature: float = 0.7


class UpdateAgentPromptCommand(BaseModel):
    agent_id: UUID
    name: str
    prompt: str
    description: str
    temperature: float


class PatchAgentPromptCommand(BaseModel):
    agent_id: UUID
    name: str | None = None
    prompt: str | None = None
    description: str | None = None
    temperature: float | None = None
