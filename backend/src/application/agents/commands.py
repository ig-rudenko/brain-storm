from pydantic import BaseModel


class CreateAgentCommand(BaseModel):
    name: str
    description: str
    prompt: str
    temperature: float = 0.7


class UpdateAgentPromptCommand(BaseModel):
    agent_id: str
    new_prompt: str
