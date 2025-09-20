from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from src.application.pipelines.commands import RunPipelineCommand
from src.application.pipelines.handlers import PipelineHandler
from src.application.users.dto import UserDTO
from src.domain.common.exceptions import DomainError
from src.domain.pipelines.entities import Pipeline

from ..auth import get_current_user
from ..dependencies import get_pipeline_handler
from ..schemas.message import MessageSchema, MessagesResponseSchema
from ..schemas.pipelines import (
    PipelineCreateSchema,
    PipelineReadSchema,
    RunPipelineSchema,
)

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.post("", response_model=PipelineReadSchema)
async def create_pipeline(
    data: PipelineCreateSchema,
    user: UserDTO = Depends(get_current_user),
    pipeline_handler: PipelineHandler = Depends(get_pipeline_handler),
):
    try:
        pipeline = Pipeline.model_validate(data.model_dump())
        print(pipeline)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    try:
        pipeline = await pipeline_handler.handle_create_pipeline(pipeline)
    except DomainError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return PipelineReadSchema.model_validate(pipeline.model_dump())


@router.post("/run", response_model=MessagesResponseSchema)
async def run_pipeline(
    data: RunPipelineSchema,
    user: UserDTO = Depends(get_current_user),
    pipeline_handler: PipelineHandler = Depends(get_pipeline_handler),
):
    try:
        messages = await pipeline_handler.handle_run_pipeline(
            RunPipelineCommand(
                pipeline_id=data.pipeline_id,
                dialog_id=data.dialog_id,
                user_id=user.id,
                user_message=data.message,
            )
        )
        return MessagesResponseSchema(result=[MessageSchema.model_validate(msg) for msg in messages])
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
