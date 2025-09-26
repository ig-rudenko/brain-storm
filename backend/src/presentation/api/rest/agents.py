from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.application.agents.commands import (
    CreateAgentCommand,
    PatchAgentPromptCommand,
    UpdateAgentPromptCommand,
)
from src.application.agents.handlers import AgentCommandHandler, AgentQueryHandler
from src.application.agents.queries import AgentsQuery
from src.application.users.dto import UserDTO
from src.domain.common.exceptions import ValidationError

from ..auth import get_admin_user
from ..dependencies import get_agent_command_handler, get_agent_query_handler
from ..schemas.agents import (
    CreateAgentSchema,
    PatchAgentSchema,
    ReadAgentSchema,
    UpdateAgentSchema,
)
from ..schemas.base import PaginatedResultSchema

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=PaginatedResultSchema[ReadAgentSchema])
async def list_agents(
    search: str | None = Query(
        None, description="Search by name and description", min_length=1, max_length=100
    ),
    temp_lt: float | None = Query(None, description="Temperature less than", ge=0.0, le=1.0),
    temp_gt: float | None = Query(None, description="Temperature greater than", ge=0.0, le=1.0),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    handler: AgentQueryHandler = Depends(get_agent_query_handler),
):
    if temp_lt and temp_gt and temp_lt > temp_gt:
        raise ValidationError("`temp_lt` must be less than or equal to `temp_gt`")
    query = AgentsQuery(
        search=search,
        temp_lt=temp_lt,
        temp_gt=temp_gt,
        page=page,
        page_size=page_size,
    )
    agents, count = await handler.handle_get_list(query)
    return PaginatedResultSchema[ReadAgentSchema](results=agents, count=count)


@router.post("", response_model=ReadAgentSchema, status_code=201)
async def create_agent(
    data: CreateAgentSchema,
    handler: AgentCommandHandler = Depends(get_agent_command_handler),
):
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
async def get_agent(
    agent_id: UUID,
    _: UserDTO = Depends(get_admin_user),
    handler: AgentQueryHandler = Depends(get_agent_query_handler),
):
    return await handler.handle_get(agent_id)


@router.put("/{agent_id}", response_model=ReadAgentSchema)
async def update_agent(
    agent_id: UUID,
    data: UpdateAgentSchema,
    _: UserDTO = Depends(get_admin_user),
    handler: AgentCommandHandler = Depends(get_agent_command_handler),
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
    _: UserDTO = Depends(get_admin_user),
    handler: AgentCommandHandler = Depends(get_agent_command_handler),
):
    cmd = PatchAgentPromptCommand(
        agent_id=agent_id,
        name=data.name,
        prompt=data.prompt,
        description=data.description,
        temperature=data.temperature,
    )
    return await handler.handle_patch(cmd)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: UUID,
    _: UserDTO = Depends(get_admin_user),
    handler: AgentCommandHandler = Depends(get_agent_command_handler),
):
    return await handler.handle_delete(agent_id)
