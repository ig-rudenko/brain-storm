from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError as PydanticValidationError

from src.application.pipelines.dto import PatchPipelineCommand
from src.application.pipelines.handlers import PipelineHandler
from src.application.users.dto import UserDTO
from src.domain.common.exceptions import (
    ObjectNotFoundError,
    ValidationError,
)
from src.domain.pipelines.entities import Pipeline

from ..auth import get_admin_user
from ..dependencies import get_pipeline_handler
from ..schemas.pipelines import (
    PipelineCreateUpdateSchema,
    PipelinePatchSchema,
    PipelineReadSchema,
)

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.post("", response_model=PipelineReadSchema, status_code=201)
async def create_pipeline(
    data: PipelineCreateUpdateSchema,
    _: UserDTO = Depends(get_admin_user),
    pipeline_handler: PipelineHandler = Depends(get_pipeline_handler),
):
    try:
        pipeline = Pipeline.model_validate(data.model_dump())
        pipeline = await pipeline_handler.handle_create(pipeline)
    except PydanticValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    return PipelineReadSchema.model_validate(pipeline.model_dump())


@router.get("/{pipeline_id}", response_model=PipelineReadSchema)
async def get_pipeline(
    pipeline_id: UUID,
    pipeline_handler: PipelineHandler = Depends(get_pipeline_handler),
):
    try:
        pipeline = await pipeline_handler.handle_get(pipeline_id)
    except ObjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return PipelineReadSchema.model_validate(pipeline.model_dump())


@router.put("/{pipeline_id}", response_model=PipelineReadSchema)
async def update_pipeline(
    pipeline_id: UUID,
    data: PipelineCreateUpdateSchema,
    _: UserDTO = Depends(get_admin_user),
    pipeline_handler: PipelineHandler = Depends(get_pipeline_handler),
):
    try:
        pipeline = Pipeline.model_validate(data.model_dump())
    except PydanticValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    pipeline.id = pipeline_id
    pipeline = await pipeline_handler.handle_update(pipeline)
    return PipelineReadSchema.model_validate(pipeline.model_dump())


@router.patch("/{pipeline_id}", response_model=PipelineReadSchema)
async def patch_pipeline(
    pipeline_id: UUID,
    data: PipelinePatchSchema,
    _: UserDTO = Depends(get_admin_user),
    pipeline_handler: PipelineHandler = Depends(get_pipeline_handler),
):
    try:
        pipeline = await pipeline_handler.handle_patch(
            PatchPipelineCommand(
                pipeline_id=pipeline_id, name=data.name, description=data.description, root=data.root
            )
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return PipelineReadSchema.model_validate(pipeline.model_dump())


@router.delete("/{pipeline_id}", status_code=204)
async def delete_pipeline(
    pipeline_id: UUID,
    _: UserDTO = Depends(get_admin_user),
    pipeline_handler: PipelineHandler = Depends(get_pipeline_handler),
):
    await pipeline_handler.handle_delete(pipeline_id)
