from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class PipelineCreateUpdateSchema(BaseModel):
    name: str = Field(..., max_length=150, title="Название пайплайна")
    description: str = ""
    root: dict[str, Any]  # сырой JSON пайплайна


class PipelineReadSchema(PipelineCreateUpdateSchema):
    id: UUID


class PipelinePatchSchema(BaseModel):
    name: str | None = Field(default=None, max_length=150, title="Название пайплайна")
    description: str | None = None
    root: dict[str, Any] | None = None


class RunPipelineSchema(BaseModel):
    pipeline_id: UUID
    dialog_id: UUID
    message: str
