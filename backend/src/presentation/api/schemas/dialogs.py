from uuid import UUID

from pydantic import BaseModel, Field


class CreateDialogSchema(BaseModel):
    pipeline_id: UUID
    name: str = Field(..., min_length=1, max_length=150)


class DialogSchema(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    agents: list[UUID]
