from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from src.domain.pipelines.entities import Pipeline

from ..schemas.pipelines import PipelineCreateSchema, PipelineReadSchema

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.post("", response_model=PipelineReadSchema)
async def create_pipeline(data: PipelineCreateSchema):
    try:
        pipeline = Pipeline.model_validate(data.model_dump())
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors())
    # await repo.add(pipeline)
    return PipelineReadSchema.model_validate(pipeline.model_dump())
