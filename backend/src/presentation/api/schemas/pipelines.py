from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel


class PipelineCreateSchema(BaseModel):
    name: str
    root: Dict[str, Any]   # сырой JSON пайплайна


class PipelineReadSchema(PipelineCreateSchema):
    id: UUID
