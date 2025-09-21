from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from src.application.pipelines.dto import PatchPipelineCommand
from src.application.pipelines.handlers import PipelineHandler
from src.application.users.dto import UserDTO
from src.domain.common.exceptions import DomainError, ObjectNotFoundError
from src.domain.pipelines.entities import Pipeline

from ..auth import get_current_user
from ..dependencies import get_pipeline_handler
from ..schemas.pipelines import PipelineCreateUpdateSchema, PipelineReadSchema, PipelinePatchSchema

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.post("", response_model=PipelineReadSchema)
async def create_pipeline(
    data: PipelineCreateUpdateSchema,
    _: UserDTO = Depends(get_current_user),
    pipeline_handler: PipelineHandler = Depends(get_pipeline_handler),
):
    try:
        pipeline = Pipeline.model_validate(data.model_dump())
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    try:
        pipeline = await pipeline_handler.handle_create(pipeline)
    except ObjectNotFoundError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except DomainError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
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
    _user: UserDTO = Depends(get_current_user),
    pipeline_handler: PipelineHandler = Depends(get_pipeline_handler),
):
    try:
        pipeline = Pipeline.model_validate(data.model_dump())
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    try:
        pipeline.id = pipeline_id
        pipeline = await pipeline_handler.handle_update(pipeline)
    except ObjectNotFoundError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except DomainError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return PipelineReadSchema.model_validate(pipeline.model_dump())


@router.patch("/{pipeline_id}", response_model=PipelineReadSchema)
async def patch_pipeline(
    pipeline_id: UUID,
    data: PipelinePatchSchema,
    _user: UserDTO = Depends(get_current_user),
    pipeline_handler: PipelineHandler = Depends(get_pipeline_handler),
):
    try:
        pipeline = await pipeline_handler.handle_patch(
            PatchPipelineCommand(
                pipeline_id=pipeline_id, name=data.name, description=data.description, root=data.root
            )
        )
    except ObjectNotFoundError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except DomainError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return PipelineReadSchema.model_validate(pipeline.model_dump())


@router.delete("/{pipeline_id}")
async def delete_pipeline(
    pipeline_id: UUID,
    _user: UserDTO = Depends(get_current_user),
    pipeline_handler: PipelineHandler = Depends(get_pipeline_handler),
):
    try:
        pipeline = await pipeline_handler.handle_delete(pipeline_id)
    except ObjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DomainError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
