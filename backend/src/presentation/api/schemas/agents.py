from uuid import UUID

from pydantic import BaseModel, Field


class UpdateAgentSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: str
    prompt: str = Field(..., min_length=2, max_length=1500)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)

    class Config:
        from_attributes = True

class CreateAgentSchema(UpdateAgentSchema):
    id: UUID


class ReadAgentSchema(UpdateAgentSchema):
    id: UUID


class PatchAgentSchema(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None)
    prompt: str | None = Field(default=None, min_length=2, max_length=1500)
    temperature: float | None = Field(default=None, ge=0.0, le=1.0)
