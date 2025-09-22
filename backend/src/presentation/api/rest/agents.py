from uuid import UUID

from fastapi import APIRouter, Depends

from src.application.agents.commands import (
    CreateAgentCommand,
    PatchAgentPromptCommand,
    UpdateAgentPromptCommand,
)
from src.application.agents.handlers import AgentCommandHandler

from ..dependencies import get_agent_handler
from ..schemas.agents import (
    CreateAgentSchema,
    PatchAgentSchema,
    ReadAgentSchema,
    UpdateAgentSchema,
)

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=ReadAgentSchema)
async def create_agent(data: CreateAgentSchema, handler: AgentCommandHandler = Depends(get_agent_handler)):
    agent = await handler.handle_create(
        CreateAgentCommand(
            agent_id=data.id,
            name=data.name,
            description=data.description,
            prompt=data.prompt,
            temperature=data.temperature,
        )
    )
    return agent


@router.get("/{agent_id}", response_model=ReadAgentSchema)
async def get_agent(agent_id: UUID, handler: AgentCommandHandler = Depends(get_agent_handler)):
    return await handler.handle_get(agent_id)


@router.put("/{agent_id}", response_model=ReadAgentSchema)
async def update_agent(
    agent_id: UUID, data: UpdateAgentSchema, handler: AgentCommandHandler = Depends(get_agent_handler)
):
    cmd = UpdateAgentPromptCommand(
        agent_id=agent_id,
        name=data.name,
        prompt=data.prompt,
        description=data.description,
        temperature=data.temperature,
    )
    return await handler.handle_update(cmd)


@router.patch("/{agent_id}", response_model=ReadAgentSchema)
async def patch_agent(
    agent_id: UUID,
    data: PatchAgentSchema,
    handler: AgentCommandHandler = Depends(get_agent_handler),
):
    cmd = PatchAgentPromptCommand(
        agent_id=agent_id,
        name=data.name,
        prompt=data.prompt,
        description=data.description,
        temperature=data.temperature,
    )
    return await handler.handle_patch(cmd)


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: UUID,
    handler: AgentCommandHandler = Depends(get_agent_handler),
):
    return await handler.handle_delete(agent_id)
