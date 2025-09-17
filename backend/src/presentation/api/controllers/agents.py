from fastapi import APIRouter, Depends
from uuid import UUID
from src.application.agents.commands import CreateAgentCommand, UpdateAgentPromptCommand
from src.application.agents.handlers import AgentCommandHandler

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/")
async def create_agent(
    cmd: CreateAgentCommand,
    handler: AgentCommandHandler = Depends(),
) -> dict:
    agent_id = await handler.handle_create(cmd)
    return {"id": str(agent_id)}


@router.put("/{agent_id}/prompt")
async def update_prompt(
    agent_id: UUID,
    data: dict,
    handler: AgentCommandHandler = Depends(),
) -> dict:
    cmd = UpdateAgentPromptCommand(agent_id=str(agent_id), new_prompt=data["prompt"])
    await handler.handle_update_prompt(cmd)
    return {"status": "updated"}
