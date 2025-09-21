from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.application.agents.commands import CreateAgentCommand, UpdateAgentPromptCommand
from src.application.agents.handlers import AgentCommandHandler
from src.domain.common.exceptions import DomainError
from src.presentation.api.dependencies import get_agent_handler
from src.presentation.api.schemas.agents import CreateUpdateAgentSchema

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/")
async def create_agent(
    data: CreateUpdateAgentSchema,
    handler: AgentCommandHandler = Depends(get_agent_handler),
) -> dict:
    try:
        agent_id = await handler.handle_create(
            CreateAgentCommand(
                name=data.name,
                description=data.description,
                prompt=data.prompt,
                temperature=data.temperature,
            )
        )
    except DomainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"id": str(agent_id)}


@router.put("/{agent_id}")
async def update_prompt(
    agent_id: UUID,
    data: dict,
    handler: AgentCommandHandler = Depends(),
) -> dict:
    cmd = UpdateAgentPromptCommand(agent_id=str(agent_id), new_prompt=data["prompt"])
    await handler.handle_update_prompt(cmd)
    return {"status": "updated"}
