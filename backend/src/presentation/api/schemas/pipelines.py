from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class PipelineCreateSchema(BaseModel):
    name: str = Field(..., max_length=150, title="Название пайплайна")
    description: str = ""
    root: dict[str, Any]  # сырой JSON пайплайна


class PipelineReadSchema(PipelineCreateSchema):
    id: UUID


class RunPipelineSchema(BaseModel):
    pipeline_id: UUID
    dialog_id: UUID
    message: str
